//! # Hyperdimensional Arithmetic Engine
//!
//! Mathematical cognition using hyperdimensional computing primitives.
//! Implements Peano-style number construction and arithmetic operations.

use symthaea_core::hdc::RealHV;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Hyperdimensional number representation
#[derive(Debug, Clone)]
pub struct HdcNumber {
    /// The hypervector encoding
    pub encoding: RealHV,
    /// Numeric value (if known)
    pub value: Option<i64>,
    /// Confidence in encoding
    pub confidence: f32,
}

impl HdcNumber {
    /// Create zero
    pub fn zero(dimension: usize) -> Self {
        Self {
            encoding: RealHV::random(dimension),
            value: Some(0),
            confidence: 1.0,
        }
    }

    /// Create from integer
    pub fn from_int(n: i64, dimension: usize) -> Self {
        // Use successive bundling to create Peano-style encoding
        let base = RealHV::random(dimension);
        let mut encoding = base.clone();

        for _ in 0..n.abs() {
            let successor = RealHV::random(dimension);
            encoding = encoding.bundle(&[successor]);
        }

        Self {
            encoding,
            value: Some(n),
            confidence: 1.0,
        }
    }

    /// Successor function (n + 1)
    pub fn successor(&self, successor_hv: &RealHV) -> Self {
        Self {
            encoding: self.encoding.bundle(&[successor_hv.clone()]),
            value: self.value.map(|v| v + 1),
            confidence: self.confidence * 0.99,
        }
    }
}

/// Result of arithmetic operation
#[derive(Debug, Clone)]
pub struct ArithmeticResult {
    /// Resulting number
    pub result: HdcNumber,
    /// Operation performed
    pub operation: String,
    /// Steps taken
    pub steps: Vec<String>,
    /// Confidence in result
    pub confidence: f32,
}

/// Main arithmetic engine
pub struct ArithmeticEngine {
    /// Dimension
    dimension: usize,
    /// Successor hypervector (shared across operations)
    successor_hv: RealHV,
    /// Cache of computed numbers
    cache: HashMap<i64, HdcNumber>,
    /// Statistics
    operations_count: u64,
}

impl ArithmeticEngine {
    /// Create new engine
    pub fn new(dimension: usize) -> Self {
        Self {
            dimension,
            successor_hv: RealHV::random(dimension),
            cache: HashMap::new(),
            operations_count: 0,
        }
    }

    /// Encode an integer
    pub fn encode(&mut self, n: i64) -> HdcNumber {
        if let Some(cached) = self.cache.get(&n) {
            return cached.clone();
        }

        let num = HdcNumber::from_int(n, self.dimension);
        self.cache.insert(n, num.clone());
        num
    }

    /// Add two numbers
    pub fn add(&mut self, a: &HdcNumber, b: &HdcNumber) -> ArithmeticResult {
        self.operations_count += 1;

        // Use value if known
        let result_value = match (a.value, b.value) {
            (Some(av), Some(bv)) => Some(av + bv),
            _ => None,
        };

        // Bundle the encodings
        let result_encoding = a.encoding.bundle(&[b.encoding.clone()]);

        ArithmeticResult {
            result: HdcNumber {
                encoding: result_encoding,
                value: result_value,
                confidence: a.confidence * b.confidence,
            },
            operation: "add".to_string(),
            steps: vec![
                format!("Bundled encodings for {:?} + {:?}", a.value, b.value),
            ],
            confidence: a.confidence * b.confidence,
        }
    }

    /// Multiply two numbers
    pub fn multiply(&mut self, a: &HdcNumber, b: &HdcNumber) -> ArithmeticResult {
        self.operations_count += 1;

        let result_value = match (a.value, b.value) {
            (Some(av), Some(bv)) => Some(av * bv),
            _ => None,
        };

        // Use binding for multiplication (permute + bundle)
        let permuted_b = b.encoding.permute(1);
        let result_encoding = a.encoding.bind(&permuted_b);

        ArithmeticResult {
            result: HdcNumber {
                encoding: result_encoding,
                value: result_value,
                confidence: a.confidence * b.confidence * 0.95,
            },
            operation: "multiply".to_string(),
            steps: vec![
                format!("Bound encodings for {:?} * {:?}", a.value, b.value),
            ],
            confidence: a.confidence * b.confidence * 0.95,
        }
    }

    /// Compare two numbers
    pub fn compare(&self, a: &HdcNumber, b: &HdcNumber) -> f32 {
        a.encoding.cosine_similarity(&b.encoding)
    }

    /// Get statistics
    pub fn operations_count(&self) -> u64 {
        self.operations_count
    }
}

impl Default for ArithmeticEngine {
    fn default() -> Self {
        Self::new(512)
    }
}

/// Symbolic expression for algebra
#[derive(Debug, Clone)]
pub enum SymbolicExpr {
    /// A constant value
    Const(f64),
    /// A variable
    Var(String),
    /// Addition
    Add(Box<SymbolicExpr>, Box<SymbolicExpr>),
    /// Subtraction
    Sub(Box<SymbolicExpr>, Box<SymbolicExpr>),
    /// Multiplication
    Mul(Box<SymbolicExpr>, Box<SymbolicExpr>),
    /// Division
    Div(Box<SymbolicExpr>, Box<SymbolicExpr>),
    /// Power
    Pow(Box<SymbolicExpr>, Box<SymbolicExpr>),
}

impl SymbolicExpr {
    /// Evaluate with variable assignments
    pub fn evaluate(&self, vars: &HashMap<String, f64>) -> Option<f64> {
        match self {
            SymbolicExpr::Const(c) => Some(*c),
            SymbolicExpr::Var(name) => vars.get(name).copied(),
            SymbolicExpr::Add(a, b) => {
                Some(a.evaluate(vars)? + b.evaluate(vars)?)
            }
            SymbolicExpr::Sub(a, b) => {
                Some(a.evaluate(vars)? - b.evaluate(vars)?)
            }
            SymbolicExpr::Mul(a, b) => {
                Some(a.evaluate(vars)? * b.evaluate(vars)?)
            }
            SymbolicExpr::Div(a, b) => {
                let divisor = b.evaluate(vars)?;
                if divisor.abs() < 1e-10 {
                    None
                } else {
                    Some(a.evaluate(vars)? / divisor)
                }
            }
            SymbolicExpr::Pow(base, exp) => {
                Some(base.evaluate(vars)?.powf(exp.evaluate(vars)?))
            }
        }
    }
}

/// Polynomial representation
#[derive(Debug, Clone)]
pub struct Polynomial {
    /// Coefficients (index = power)
    pub coefficients: Vec<f64>,
}

impl Polynomial {
    /// Create from coefficients
    pub fn new(coefficients: Vec<f64>) -> Self {
        Self { coefficients }
    }

    /// Evaluate at point
    pub fn evaluate(&self, x: f64) -> f64 {
        let mut result = 0.0;
        let mut power = 1.0;
        for coeff in &self.coefficients {
            result += coeff * power;
            power *= x;
        }
        result
    }

    /// Degree of polynomial
    pub fn degree(&self) -> usize {
        if self.coefficients.is_empty() {
            0
        } else {
            self.coefficients.len() - 1
        }
    }

    /// Compute the formal derivative d/dx of this polynomial.
    ///
    /// Coefficients `[a₀, a₁, a₂, a₃, ...]` become `[a₁, 2a₂, 3a₃, ...]`.
    pub fn derivative(&self) -> Self {
        if self.coefficients.len() <= 1 {
            return Self::new(vec![0.0]);
        }
        let coeffs: Vec<f64> = self.coefficients.iter()
            .enumerate()
            .skip(1)
            .map(|(i, &c)| c * i as f64)
            .collect();
        Self::new(coeffs)
    }

    /// Format as human-readable polynomial string (e.g., "2x + 3x^2").
    pub fn to_string_pretty(&self) -> String {
        const EPSILON: f64 = 1e-10;
        if self.coefficients.is_empty() || self.coefficients.iter().all(|&c| c.abs() < EPSILON) {
            return "0".to_string();
        }

        let mut terms = Vec::new();
        for (i, &coeff) in self.coefficients.iter().enumerate() {
            if coeff.abs() < EPSILON {
                continue;
            }
            let term = match i {
                0 => format!("{}", coeff),
                1 => {
                    if coeff == 1.0 {
                        "x".to_string()
                    } else if coeff == -1.0 {
                        "-x".to_string()
                    } else {
                        format!("{}x", coeff)
                    }
                }
                _ => {
                    if coeff == 1.0 {
                        format!("x^{}", i)
                    } else if coeff == -1.0 {
                        format!("-x^{}", i)
                    } else {
                        format!("{}x^{}", coeff, i)
                    }
                }
            };
            terms.push(term);
        }

        if terms.is_empty() {
            "0".to_string()
        } else {
            terms.join(" + ").replace(" + -", " - ")
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_hdc_number() {
        let num = HdcNumber::from_int(5, 512);
        assert_eq!(num.value, Some(5));
    }

    #[test]
    fn test_arithmetic_add() {
        let mut engine = ArithmeticEngine::new(512);
        let a = engine.encode(3);
        let b = engine.encode(4);
        let result = engine.add(&a, &b);
        assert_eq!(result.result.value, Some(7));
    }

    #[test]
    fn test_polynomial() {
        // 2 + 3x + x^2
        let poly = Polynomial::new(vec![2.0, 3.0, 1.0]);
        assert!((poly.evaluate(2.0) - 12.0).abs() < 1e-10);
    }

    #[test]
    fn test_polynomial_derivative() {
        // x^2 → 2x
        let poly = Polynomial::new(vec![0.0, 0.0, 1.0]);
        let deriv = poly.derivative();
        assert_eq!(deriv.coefficients.len(), 1);
        assert!((deriv.coefficients[0] - 2.0).abs() < 1e-10);
        assert!(deriv.to_string_pretty().contains("2x"));

        // 3 + 2x + 5x^2 → 2 + 10x
        let poly2 = Polynomial::new(vec![3.0, 2.0, 5.0]);
        let deriv2 = poly2.derivative();
        assert_eq!(deriv2.coefficients.len(), 2);
        assert!((deriv2.coefficients[0] - 2.0).abs() < 1e-10);
        assert!((deriv2.coefficients[1] - 10.0).abs() < 1e-10);

        // Constant → 0
        let constant = Polynomial::new(vec![42.0]);
        let deriv_c = constant.derivative();
        assert_eq!(deriv_c.coefficients.len(), 1);
        assert!((deriv_c.coefficients[0]).abs() < 1e-10);
    }

    #[test]
    fn test_polynomial_pretty_print() {
        let poly = Polynomial::new(vec![0.0, 0.0, 1.0]); // x^2
        assert_eq!(poly.to_string_pretty(), "x^2");

        let poly2 = Polynomial::new(vec![3.0, 2.0, 5.0]); // 3 + 2x + 5x^2
        let s = poly2.to_string_pretty();
        assert!(s.contains("3"));
        assert!(s.contains("2x"));
        assert!(s.contains("5x^2"));
    }
}
