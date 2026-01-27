//! Mathematics Domain Plugin
//!
//! Provides domain-specific language processing for mathematical content:
//! number extraction, operator recognition, expression validation, and
//! math-oriented intent prototypes.
//!
//! This plugin directly supports the positive prototypes built for math
//! confidence boosting in Symthaea's HDC-based intent classification.

use std::collections::HashMap;
use std::sync::Mutex;

use super::domain_plugin::{
    ComputedResult, DomainPlugin, DomainPrompts, Entity, ErrorDiagnosis as DomainErrorDiagnosis,
    IntentPrototypes, RiskLevel, ValidationResult,
};
use crate::hdc::arithmetic_engine::MathReasoningBridge;
use crate::mind::structured_thought::{EpistemicCube, ETier, NTier, MTier};

// ============================================================================
// MATH KEYWORDS & PATTERNS
// ============================================================================

/// Keywords that indicate mathematical domain content
const MATH_KEYWORDS: &[&str] = &[
    "calculate", "compute", "solve", "evaluate", "simplify",
    "factor", "expand", "derive", "differentiate", "integrate",
    "sum", "product", "limit", "series", "sequence", "derivative", "integral",
    "equation", "inequality", "expression", "formula", "function",
    "variable", "constant", "coefficient", "exponent", "logarithm",
    "matrix", "vector", "determinant", "eigenvalue", "eigenvector",
    "theorem", "proof", "lemma", "corollary", "axiom",
    "prime", "divisor", "modulo", "remainder", "factorial",
    "trigonometry", "sine", "cosine", "tangent", "radian",
    "polynomial", "quadratic", "linear", "cubic", "exponential",
    "algebra", "calculus", "geometry", "topology", "statistics",
    "probability", "combinatorics", "number theory", "graph theory",
    "mean", "median", "mode", "variance", "standard deviation",
    "hypothesis", "distribution", "permutation", "combination",
    "set", "subset", "union", "intersection", "complement",
    "pi", "infinity", "sqrt", "square root", "absolute value",
];

/// Mathematical operators and symbols (as text)
const MATH_OPERATORS: &[&str] = &[
    "+", "-", "*", "/", "^", "=", "<", ">", "<=", ">=",
    "!=", "mod", "div", "sqrt", "log", "ln", "sin", "cos", "tan",
    "abs", "min", "max", "sum", "prod",
];

// ============================================================================
// MATH DOMAIN PLUGIN
// ============================================================================

/// Mathematics domain plugin for Symthaea's language processing system
///
/// Extracts numbers, operators, and mathematical expressions from user input.
/// Provides intent prototypes for calculation, proof, and definition queries.
/// Uses `MathReasoningBridge` to compute arithmetic results via the HDC engine.
pub struct MathPlugin {
    bridge: Mutex<MathReasoningBridge>,
}

impl MathPlugin {
    /// Create a new MathPlugin with an initialized MathReasoningBridge.
    pub fn new() -> Self {
        Self {
            bridge: Mutex::new(MathReasoningBridge::new()),
        }
    }
}

impl DomainPlugin for MathPlugin {
    fn domain_name(&self) -> &str {
        "mathematics"
    }

    fn extract_entities(&self, text: &str) -> Vec<Entity> {
        let mut entities = Vec::new();

        // Extract numbers (integers and decimals, including negative)
        let mut i = 0;
        let chars: Vec<char> = text.chars().collect();
        while i < chars.len() {
            // Check for start of a number
            let is_negative = chars[i] == '-'
                && i + 1 < chars.len()
                && chars[i + 1].is_ascii_digit()
                && (i == 0 || !chars[i - 1].is_alphanumeric());

            if chars[i].is_ascii_digit() || is_negative {
                let start = i;
                if is_negative {
                    i += 1;
                }
                let mut has_dot = false;
                while i < chars.len() && (chars[i].is_ascii_digit() || (chars[i] == '.' && !has_dot)) {
                    if chars[i] == '.' {
                        has_dot = true;
                    }
                    i += 1;
                }
                let value: String = chars[start..i].iter().collect();
                // Skip if it looks like part of a word (e.g., "x2")
                if start == 0 || !chars[start - 1].is_alphabetic() {
                    entities.push(
                        Entity::new("number", &value, start, i)
                            .with_confidence(0.95)
                            .with_metadata("numeric_type", if has_dot { "float" } else { "integer" }),
                    );
                }
                continue;
            }
            i += 1;
        }

        // Extract operators
        for op in MATH_OPERATORS {
            if op.len() == 1 {
                // Single-char operators: match directly
                for (idx, _) in text.match_indices(op) {
                    // Avoid matching '-' as operator if it's part of a number
                    if *op == "-" {
                        if idx + 1 < text.len() {
                            let next_char = text.as_bytes()[idx + 1];
                            if next_char.is_ascii_digit() && (idx == 0 || !text.as_bytes()[idx - 1].is_ascii_digit()) {
                                continue;
                            }
                        }
                    }
                    entities.push(
                        Entity::new("operator", *op, idx, idx + op.len())
                            .with_confidence(0.9),
                    );
                }
            } else {
                // Multi-char operators: match as whole words
                let lower = text.to_lowercase();
                for (idx, _) in lower.match_indices(op) {
                    // Check word boundary
                    let before_ok = idx == 0
                        || !text.as_bytes()[idx - 1].is_ascii_alphanumeric();
                    let after_ok = idx + op.len() >= text.len()
                        || !text.as_bytes()[idx + op.len()].is_ascii_alphanumeric();
                    if before_ok && after_ok {
                        entities.push(
                            Entity::new("operator", *op, idx, idx + op.len())
                                .with_confidence(0.85),
                        );
                    }
                }
            }
        }

        // Extract mathematical terms (keywords found in text)
        let lower = text.to_lowercase();
        for keyword in MATH_KEYWORDS {
            if keyword.len() < 3 {
                continue; // Skip very short keywords to avoid false positives
            }
            for (idx, _) in lower.match_indices(keyword) {
                // Word boundary check
                let before_ok = idx == 0
                    || !lower.as_bytes()[idx - 1].is_ascii_alphanumeric();
                let after_ok = idx + keyword.len() >= lower.len()
                    || !lower.as_bytes()[idx + keyword.len()].is_ascii_alphanumeric();
                if before_ok && after_ok {
                    entities.push(
                        Entity::new("math_term", *keyword, idx, idx + keyword.len())
                            .with_confidence(0.8)
                            .with_metadata("category", categorize_math_term(keyword)),
                    );
                }
            }
        }

        entities
    }

    fn intent_prototypes(&self) -> IntentPrototypes {
        let mut prototypes = IntentPrototypes::default();

        // Math-specific command intents
        prototypes.command = vec![
            "calculate", "compute", "solve", "evaluate", "simplify",
            "factor", "expand", "derive", "integrate", "plot",
            "prove", "verify", "check", "convert", "approximate",
        ].into_iter().map(String::from).collect();

        // Math-specific question intents
        prototypes.question = vec![
            "what is", "how to solve", "what does", "why does",
            "is it true", "can you prove", "what are the roots",
            "what is the derivative", "what is the integral",
            "how many", "what is the value", "is this correct",
            "what formula", "which theorem",
        ].into_iter().map(String::from).collect();

        // Math-specific complaint intents
        prototypes.complaint = vec![
            "wrong answer", "incorrect", "does not equal",
            "undefined", "division by zero", "overflow",
            "does not converge", "no solution", "complex number",
        ].into_iter().map(String::from).collect();

        // Custom intents for mathematics
        let mut custom = HashMap::new();
        custom.insert("calculation".to_string(), vec![
            "calculate".to_string(),
            "compute".to_string(),
            "evaluate".to_string(),
            "what is".to_string(),
            "find the value".to_string(),
        ]);
        custom.insert("proof".to_string(), vec![
            "prove".to_string(),
            "show that".to_string(),
            "demonstrate".to_string(),
            "verify".to_string(),
            "by induction".to_string(),
            "by contradiction".to_string(),
        ]);
        custom.insert("definition".to_string(), vec![
            "define".to_string(),
            "what is a".to_string(),
            "definition of".to_string(),
            "meaning of".to_string(),
            "explain".to_string(),
        ]);
        prototypes.custom = custom;

        prototypes
    }

    fn prompts(&self) -> DomainPrompts {
        DomainPrompts {
            system: "You are a mathematical reasoning assistant. \
                     Provide clear, step-by-step solutions. \
                     Show your work and cite relevant theorems."
                .to_string(),
            clarification: "Could you clarify the mathematical expression? \
                           Specifically: '{}'"
                .to_string(),
            action_confirm: "I'll work through this mathematical problem: {}"
                .to_string(),
            error_explain: "There's a mathematical issue: {}. \
                           Let me explain why."
                .to_string(),
            out_of_domain: "That doesn't appear to be a mathematics question. \
                           I'm specialized in mathematical reasoning. {}"
                .to_string(),
        }
    }

    fn diagnose_error(&self, error_text: &str) -> Option<DomainErrorDiagnosis> {
        let lower = error_text.to_lowercase();

        if lower.contains("division by zero") || lower.contains("divide by zero") {
            return Some(DomainErrorDiagnosis {
                category: "arithmetic".to_string(),
                error_type: "division_by_zero".to_string(),
                description: "Division by zero is undefined".to_string(),
                suggestion: Some("Check that the denominator is non-zero before dividing".to_string()),
                confidence: 0.95,
                risk_level: RiskLevel::Safe,
                location: None,
            });
        }

        if lower.contains("overflow") || lower.contains("too large") {
            return Some(DomainErrorDiagnosis {
                category: "arithmetic".to_string(),
                error_type: "overflow".to_string(),
                description: "Numeric overflow: the result exceeds representable range".to_string(),
                suggestion: Some("Use arbitrary-precision arithmetic or reduce the magnitude of inputs".to_string()),
                confidence: 0.85,
                risk_level: RiskLevel::Low,
                location: None,
            });
        }

        if lower.contains("undefined") || lower.contains("not defined") {
            return Some(DomainErrorDiagnosis {
                category: "domain_error".to_string(),
                error_type: "undefined_result".to_string(),
                description: "The expression is undefined for the given input".to_string(),
                suggestion: Some("Check the domain of the function; some inputs may be out of range".to_string()),
                confidence: 0.75,
                risk_level: RiskLevel::Safe,
                location: None,
            });
        }

        if lower.contains("no solution") || lower.contains("inconsistent") {
            return Some(DomainErrorDiagnosis {
                category: "algebra".to_string(),
                error_type: "no_solution".to_string(),
                description: "The equation or system has no solution".to_string(),
                suggestion: Some("Verify the equation is correctly stated; the system may be inconsistent".to_string()),
                confidence: 0.8,
                risk_level: RiskLevel::Safe,
                location: None,
            });
        }

        None
    }

    fn validate_input(&self, input: &str) -> ValidationResult {
        let mut errors = Vec::new();
        let mut warnings = Vec::new();
        let mut suggestions = Vec::new();

        // Check for balanced parentheses
        let open_parens = input.matches('(').count();
        let close_parens = input.matches(')').count();
        if open_parens != close_parens {
            errors.push(format!(
                "Mismatched parentheses: {} opening vs {} closing",
                open_parens, close_parens
            ));
            suggestions.push("Check that every '(' has a matching ')'".to_string());
        }

        // Check for empty expressions between operators
        if input.contains("++") || input.contains("**") || input.contains("//") {
            warnings.push("Consecutive operators detected; this may be unintentional".to_string());
        }

        // Check for trailing operators
        let trimmed = input.trim();
        if !trimmed.is_empty() {
            let last_char = trimmed.chars().last().unwrap();
            if ['+', '-', '*', '/', '^'].contains(&last_char) {
                warnings.push("Expression ends with an operator; it may be incomplete".to_string());
            }
        }

        if errors.is_empty() {
            let mut result = ValidationResult::valid();
            result.warnings = warnings;
            result.suggestions = suggestions;
            result
        } else {
            let mut result = ValidationResult::invalid(errors);
            result.warnings = warnings;
            result.suggestions = suggestions;
            result
        }
    }

    fn is_in_domain(&self, topic: &str) -> f64 {
        let lower = topic.to_lowercase();
        let mut score: f64 = 0.0;
        let mut keyword_matches = 0;

        // Check for math keywords
        for keyword in MATH_KEYWORDS {
            if keyword.len() < 3 {
                continue;
            }
            if lower.contains(keyword) {
                keyword_matches += 1;
                // Strong indicators
                if ["calculate", "equation", "theorem", "proof", "integral",
                    "derivative", "algebra", "calculus", "matrix", "polynomial"]
                    .contains(keyword)
                {
                    score += 0.35;
                } else {
                    score += 0.12;
                }
            }
        }

        // Check for mathematical operators and numbers
        let has_operators = lower.contains('+') || lower.contains('*')
            || lower.contains('/') || lower.contains('^')
            || lower.contains('=');
        let has_numbers = lower.chars().any(|c| c.is_ascii_digit());

        if has_operators && has_numbers {
            score += 0.25;
        } else if has_operators || has_numbers {
            score += 0.1;
        }

        if keyword_matches > 0 {
            (0.55 + score).min(1.0)
        } else if has_operators && has_numbers {
            0.4
        } else {
            0.1
        }
    }

    fn vocabulary(&self) -> Vec<String> {
        let mut vocab: Vec<String> = MATH_KEYWORDS.iter().map(|s| s.to_string()).collect();
        vocab.extend(MATH_OPERATORS.iter().map(|s| s.to_string()));
        vocab
    }

    fn preprocess(&self, input: &str) -> String {
        // Normalize common math notations
        input
            .replace("squared", "^2")
            .replace("cubed", "^3")
            .replace("square root of", "sqrt")
            .replace(" times ", " * ")
            .replace(" divided by ", " / ")
            .replace(" plus ", " + ")
            .replace(" minus ", " - ")
            .replace(" to the power of ", "^")
    }

    fn suggest_actions(&self, context: &str) -> Vec<String> {
        let lower = context.to_lowercase();
        let mut actions = Vec::new();

        if lower.contains("solve") || lower.contains("equation") {
            actions.push("Isolate the variable on one side".to_string());
            actions.push("Check for extraneous solutions".to_string());
        }
        if lower.contains("prove") || lower.contains("theorem") {
            actions.push("State the hypothesis and conclusion clearly".to_string());
            actions.push("Consider proof by contradiction or induction".to_string());
        }
        if lower.contains("calculate") || lower.contains("compute") {
            actions.push("Break the expression into simpler parts".to_string());
            actions.push("Verify with an alternative method".to_string());
        }
        if lower.contains("graph") || lower.contains("plot") {
            actions.push("Identify the domain and range".to_string());
            actions.push("Find critical points and asymptotes".to_string());
        }

        actions
    }

    fn compute(&self, input: &str, entities: &[Entity]) -> Option<ComputedResult> {
        // All math computations are axiomatic, reproducible, and foundational
        let math_cube = EpistemicCube {
            e: ETier::E4,
            n: NTier::N3,
            m: MTier::M3,
        };

        // Try arithmetic: look for (number, operator, number) pattern
        let numbers: Vec<&Entity> = entities.iter()
            .filter(|e| e.entity_type == "number")
            .collect();
        let operators: Vec<&Entity> = entities.iter()
            .filter(|e| e.entity_type == "operator")
            .collect();

        if numbers.len() == 2 && operators.len() == 1 {
            let a: u64 = match numbers[0].value.parse() {
                Ok(v) => v,
                Err(_) => return None,
            };
            let b: u64 = match numbers[1].value.parse() {
                Ok(v) => v,
                Err(_) => return None,
            };
            let op = operators[0].value.as_str();

            if let Ok(mut bridge) = self.bridge.lock() {
                let assertion = bridge.assert_equality(a, b, op);
                // Only return if the operation was valid (confidence > 0)
                if assertion.confidence > 0.0 && !assertion.object.starts_with("undefined") && assertion.object != "unknown operation" {
                    let op_display = match op {
                        "+" | "add" => "+",
                        "-" | "subtract" => "-",
                        "*" | "×" | "multiply" => "*",
                        "/" | "÷" | "divide" => "/",
                        "%" | "mod" => "%",
                        "^" | "power" => "^",
                        other => other,
                    };
                    return Some(ComputedResult {
                        answer: format!("{} {} {} = {}", a, op_display, b, assertion.object),
                        cube: math_cube,
                        phi: assertion.phi,
                        proof_available: assertion.proof_source.is_some(),
                    });
                }
            }
        }

        // Try symbolic derivative: "derivative of x^N" pattern
        let lower = input.to_lowercase();
        if lower.contains("derivative") {
            if let Some((poly_str, deriv_str)) = Self::compute_derivative_from_text(&lower) {
                return Some(ComputedResult {
                    answer: format!("d/dx [{}] = {}", poly_str, deriv_str),
                    cube: math_cube,
                    phi: 0.0,
                    proof_available: false,
                });
            }
        }

        None
    }
}

impl MathPlugin {
    /// Compute the derivative of a simple polynomial from natural language.
    ///
    /// Handles patterns like "x^2" → "2x", "x^3" → "3x^2", etc.
    /// Returns `(original_string, derivative_string)`.
    fn compute_derivative_from_text(text: &str) -> Option<(String, String)> {
        // Match "x^N" pattern
        if let Some(cap_pos) = text.find("x^") {
            let after = &text[cap_pos + 2..];
            let exp_str: String = after.chars().take_while(|c| c.is_ascii_digit()).collect();
            if let Ok(exp) = exp_str.parse::<u32>() {
                if exp > 0 && exp <= 20 {
                    let original = format!("x^{}", exp);
                    let derivative = if exp == 1 {
                        "1".to_string()
                    } else if exp == 2 {
                        "2x".to_string()
                    } else {
                        format!("{}x^{}", exp, exp - 1)
                    };
                    return Some((original, derivative));
                }
            }
        }

        None
    }
}

/// Categorize a math term into a sub-field
fn categorize_math_term(term: &str) -> &'static str {
    match term {
        "sine" | "cosine" | "tangent" | "radian" | "trigonometry" => "trigonometry",
        "matrix" | "vector" | "determinant" | "eigenvalue" | "eigenvector" => "linear_algebra",
        "derivative" | "differentiate" | "integrate" | "integral" | "limit" | "calculus" => "calculus",
        "prime" | "divisor" | "modulo" | "factorial" | "number theory" => "number_theory",
        "probability" | "statistics" | "mean" | "median" | "mode" | "variance" | "standard deviation" | "distribution" => "statistics",
        "set" | "subset" | "union" | "intersection" | "complement" => "set_theory",
        "polynomial" | "quadratic" | "linear" | "cubic" | "algebra" | "equation" => "algebra",
        "permutation" | "combination" | "combinatorics" => "combinatorics",
        "topology" | "geometry" => "geometry",
        _ => "general",
    }
}

// ============================================================================
// TESTS
// ============================================================================

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_domain_name() {
        let plugin = MathPlugin::new();
        assert_eq!(plugin.domain_name(), "mathematics");
    }

    #[test]
    fn test_number_extraction() {
        let plugin = MathPlugin::new();

        let entities = plugin.extract_entities("What is 42 + 3.14?");
        let numbers: Vec<&Entity> = entities.iter()
            .filter(|e| e.entity_type == "number")
            .collect();
        assert!(numbers.len() >= 2);
        assert!(numbers.iter().any(|e| e.value == "42"));
        assert!(numbers.iter().any(|e| e.value == "3.14"));
    }

    #[test]
    fn test_math_term_extraction() {
        let plugin = MathPlugin::new();

        let entities = plugin.extract_entities("Find the derivative of this polynomial");
        let terms: Vec<&Entity> = entities.iter()
            .filter(|e| e.entity_type == "math_term")
            .collect();
        assert!(terms.iter().any(|e| e.value == "derivative"));
        assert!(terms.iter().any(|e| e.value == "polynomial"));
    }

    #[test]
    fn test_domain_detection() {
        let plugin = MathPlugin::new();

        assert!(plugin.is_in_domain("Calculate the integral of x^2") > 0.6);
        assert!(plugin.is_in_domain("Solve this quadratic equation") > 0.6);
        assert!(plugin.is_in_domain("What is the weather today?") < 0.3);
    }

    #[test]
    fn test_validation() {
        let plugin = MathPlugin::new();

        let result = plugin.validate_input("(3 + 4) * 2");
        assert!(result.valid);

        let result = plugin.validate_input("(3 + 4 * 2");
        assert!(!result.valid);
    }

    #[test]
    fn test_error_diagnosis() {
        let plugin = MathPlugin::new();

        let diag = plugin.diagnose_error("Error: division by zero");
        assert!(diag.is_some());
        assert_eq!(diag.unwrap().error_type, "division_by_zero");
    }

    #[test]
    fn test_preprocess() {
        let plugin = MathPlugin::new();
        let result = plugin.preprocess("3 squared plus 4 squared");
        assert!(result.contains("^2"));
    }

    #[test]
    fn test_compute_arithmetic_via_bridge() {
        let plugin = MathPlugin::new();
        let entities = vec![
            Entity::new("number", "2", 0, 1).with_confidence(0.95),
            Entity::new("operator", "+", 2, 3).with_confidence(0.9),
            Entity::new("number", "2", 4, 5).with_confidence(0.95),
        ];
        let result = plugin.compute("What is 2+2?", &entities);
        assert!(result.is_some(), "Should compute 2+2");
        let cr = result.unwrap();
        assert!(cr.answer.contains("4"), "Answer should contain 4, got: {}", cr.answer);
        assert_eq!(cr.cube.e, ETier::E4);
        assert_eq!(cr.cube.n, NTier::N3);
        assert_eq!(cr.cube.m, MTier::M3);
    }

    #[test]
    fn test_compute_natural_language() {
        let plugin = MathPlugin::new();
        let entities = vec![
            Entity::new("number", "10", 0, 2).with_confidence(0.95),
            Entity::new("operator", "*", 3, 4).with_confidence(0.9),
            Entity::new("number", "5", 5, 6).with_confidence(0.95),
        ];
        let result = plugin.compute("What is 10 * 5?", &entities);
        assert!(result.is_some());
        let cr = result.unwrap();
        assert!(cr.answer.contains("50"), "Answer should contain 50, got: {}", cr.answer);
        assert_eq!(cr.cube.e, ETier::E4);
    }

    #[test]
    fn test_compute_symbolic_derivative() {
        let plugin = MathPlugin::new();
        let entities = vec![
            Entity::new("math_term", "derivative", 0, 10).with_confidence(0.8),
        ];
        let result = plugin.compute("What is the derivative of x^2?", &entities);
        assert!(result.is_some(), "Should compute derivative of x^2");
        let cr = result.unwrap();
        assert!(cr.answer.contains("2x") || cr.answer.contains("2*x"), "Derivative of x^2 should be 2x, got: {}", cr.answer);
        assert_eq!(cr.cube, EpistemicCube { e: ETier::E4, n: NTier::N3, m: MTier::M3 });
    }

    #[test]
    fn test_compute_non_computable_returns_none() {
        let plugin = MathPlugin::new();
        let entities = vec![
            Entity::new("math_term", "theorem", 0, 7).with_confidence(0.8),
        ];
        let result = plugin.compute("Prove the fundamental theorem of algebra", &entities);
        assert!(result.is_none(), "Non-computable queries should return None");
    }
}
