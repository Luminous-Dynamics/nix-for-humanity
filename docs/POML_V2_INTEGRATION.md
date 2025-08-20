# 📜 POML v2 Integration - Microsoft-Compliant Prompt Engineering

## 🌟 Overview

The Declarative Agent now uses **POML v2** (Prompt Optimization Markup Language), fully aligned with Microsoft's official specification. This provides transparent, governable, and reproducible prompt engineering for our AI-assisted NixOS configuration transformations.

## 🎯 Key Features

### Microsoft Specification Compliance
- ✅ Proper `<let>` variable bindings for reusable content
- ✅ Template variable substitution with `{{ }}` syntax
- ✅ Structured components: `<role>`, `<task>`, `<stepwise-instructions>`
- ✅ Examples with `<input>` and `<output>` pairs
- ✅ `<hint>` tags for performance optimization
- ✅ External document references with `<document src="..." />`

### Implementation Components

#### 1. POMLProcessor (`poml_bridge_v2.py`)
The core processor that:
- Loads and parses POML XML files
- Processes `<let>` bindings for variable definitions
- Handles template variable substitution
- Extracts components (role, task, instructions, examples)
- Builds formatted prompts from POML definitions

#### 2. POMLOrchestrator
Advanced workflow orchestration:
- Registers multiple POML prompts
- Executes multi-step workflows
- Chains prompt outputs as inputs
- Manages context across steps

#### 3. Transform Prompt v2 (`transform_prompt_v2.poml`)
The constitutional document defining:
- Agent role and expertise
- Task specifications
- Step-by-step instructions
- Input/output examples
- Safety hints and governance

## 🔧 Usage

### Basic Usage
```python
from luminous_nix.agents.poml_bridge_v2 import POMLProcessor

# Initialize processor
processor = POMLProcessor('transform_prompt_v2.poml')

# Define context
context = {
    'understanding_json': json.dumps(config_understanding),
    'user_intention': 'install firefox',
    'username': 'nixuser'
}

# Generate prompt
prompt = processor.process(context)
```

### Orchestrated Workflows
```python
from luminous_nix.agents.poml_bridge_v2 import POMLOrchestrator

# Initialize orchestrator
orchestrator = POMLOrchestrator()
orchestrator.register_prompt('transform', 'transform_prompt_v2.poml')
orchestrator.register_prompt('validate', 'validate_prompt.poml')

# Execute workflow
workflow = [
    {
        'name': 'Transform',
        'prompt': 'transform',
        'context': {'user_intention': 'install firefox'},
        'output_key': 'transformation'
    },
    {
        'name': 'Validate',
        'prompt': 'validate',
        'context': {'previous_result': '{{transformation}}'},
        'output_key': 'validation'
    }
]

results = orchestrator.create_workflow(workflow)
```

## 📝 POML v2 Syntax

### Variable Definitions
```xml
<let name="nixos_expertise">
    You are an expert NixOS system administrator...
</let>
```

### Role Definition
```xml
<role>
    {{ nixos_expertise }}
    Additional role context...
</role>
```

### Task Specification
```xml
<task>
    Transform natural language into NixOS changes
</task>
```

### Step-by-Step Instructions
```xml
<stepwise-instructions>
    <list>
        <item>Analyze the user's intention</item>
        <item>Identify NixOS attributes</item>
        <item>Generate transformations</item>
    </list>
</stepwise-instructions>
```

### Examples
```xml
<example>
    <input>install firefox</input>
    <output>
        {
            "transformations": [...],
            "confidence": 0.95
        }
    </output>
</example>
```

### Hints for Optimization
```xml
<hint>
    Remember: NixOS configurations are declarative.
    Focus on the desired end state.
</hint>
```

## 🚀 Integration with Declarative Agent

The Declarative Agent now uses POML v2 for all LLM interactions:

1. **Initialization**: Agent creates POMLProcessor and POMLOrchestrator
2. **Context Building**: Understanding + intention → POML context
3. **Prompt Generation**: POMLOrchestrator executes 'transform' prompt
4. **LLM Communication**: Generated prompt sent to LLM (when available)
5. **Response Parsing**: JSON extracted and validated per POML schema
6. **Transformation**: Results converted to TransformationSet dataclass

## 🔮 Future Enhancements

### Phase 1: LLM Integration (Next)
- Connect to local Ollama/llama.cpp
- Stream responses with progress
- Cache prompts for efficiency

### Phase 2: Advanced Workflows
- Multi-stage transformations
- Validation loops
- Human-in-the-loop confirmation

### Phase 3: Governance Dashboard
- POML prompt versioning
- A/B testing frameworks
- Performance metrics tracking

## 🎯 Benefits

1. **Transparency**: All prompts are human-readable XML
2. **Governance**: Prompts can be reviewed, versioned, and audited
3. **Reproducibility**: Same POML + context = same prompt
4. **Modularity**: Prompts can be composed and reused
5. **Compliance**: Follows Microsoft's official specification

## 📊 Testing

Run the test suite:
```bash
# Test POML processor
PYTHONPATH=src python src/luminous_nix/agents/poml_bridge_v2.py

# Test Declarative Agent with POML
PYTHONPATH=src python -c "
from luminous_nix.agents.declarative_agent import DeclarativeAgent
agent = DeclarativeAgent()
# Agent now uses POML v2 automatically
"
```

## 🌊 Sacred Reflection

The integration of POML v2 represents more than technical compliance - it's about making AI reasoning transparent and governable. Every transformation the agent performs can now be traced back to a specific prompt template, making the system auditable and trustworthy.

This aligns with our consciousness-first philosophy: technology should be transparent, not mysterious; empowering, not controlling.

---

*POML v2 Integration Complete - The agent's mind is now transparent and governable* 🌟