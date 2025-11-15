# 📖 POML Style Guide for Luminous Nix

*Prompt Optimization Modeling Language Standards and Best Practices*

## 🎯 Purpose

This guide establishes consistent patterns for writing POML templates in the Luminous Nix project, ensuring:
- **Transparency**: Users can understand AI reasoning
- **Maintainability**: Templates are easy to update
- **Reusability**: Common patterns can be shared
- **Governance**: Compliance with Microsoft POML standards
- **Testing**: Predictable structure for validation

## 📁 File Organization

```
poml/
├── templates/           # Single-purpose prompt templates
│   ├── config_*.poml   # Configuration-related prompts
│   ├── package_*.poml  # Package management prompts
│   ├── error_*.poml    # Error handling prompts
│   └── system_*.poml   # System management prompts
├── orchestrations/      # Multi-agent workflows
│   └── *.poml          # Complex multi-step operations
├── variables/           # Shared variable definitions
│   ├── common.yaml     # Common variables across templates
│   └── contexts/       # Context-specific variables
├── validators/          # POML validation tools
│   └── schema.xsd      # POML 2.0 XML schema
└── examples/           # Example usage patterns
    └── *.poml          # Documented examples
```

## 🏗️ Template Structure

### 1. Metadata Section (Required)
```xml
<metadata>
  <title>Clear, Descriptive Title</title>
  <description>What this prompt accomplishes</description>
  <author>Luminous Nix Team</author>
  <version>Semantic version (1.0.0)</version>
  <model-hints>
    <preferred-models>comma-separated list</preferred-models>
    <temperature>0.0-1.0 (lower for deterministic)</temperature>
    <max-tokens>reasonable limit</max-tokens>
  </model-hints>
</metadata>
```

### 2. Variables Section
```xml
<variables>
  <!-- Required variables -->
  <let name="required_var">{{ required_var }}</let>

  <!-- Optional with defaults -->
  <let name="optional_var">{{ optional_var | default: "value" }}</let>

  <!-- Computed variables -->
  <let name="computed">{{ var1 + var2 }}</let>
</variables>
```

### 3. Context Section
```xml
<context>
  <!-- External knowledge bases -->
  <document src="relative/path/to/knowledge.yaml" />

  <!-- Inline context (small datasets only) -->
  <data name="inline_data">
    key: value
  </data>
</context>
```

### 4. Prompt Section
```xml
<prompt>
  <system>
    System role and expertise definition.
    Keep concise and specific.
  </system>

  <stepwise-instructions>
    <!-- Logical flow of reasoning -->
    <step id="unique_id">
      Step description and actions
    </step>
  </stepwise-instructions>

  <examples>
    <!-- 2-3 representative examples -->
    <example>
      <input>Sample input</input>
      <output>Expected output</output>
    </example>
  </examples>

  <output-format>
    <!-- Structured output specification -->
  </output-format>

  <error-handling>
    <!-- Graceful failure modes -->
  </error-handling>
</prompt>
```

## 🎨 Style Conventions

### Naming Conventions
- **Files**: `snake_case.poml` (e.g., `config_analysis.poml`)
- **Variables**: `snake_case` (e.g., `user_query`)
- **Step IDs**: `snake_case` (e.g., `parse_error`)
- **Templates**: Descriptive action names (e.g., `error_resolution.poml`)

### Variable Guidelines
1. **Always provide defaults** for optional variables
2. **Use meaningful names** that describe content
3. **Document complex variables** with comments
4. **Validate variable types** in conditionals

### Conditional Logic
```xml
<!-- Simple condition -->
<if condition="variable == 'value'">
  <!-- Action -->
</if>

<!-- Multiple branches -->
<if condition="severity == 'critical'">
  <!-- Critical path -->
</if>
<elseif condition="severity == 'warning'">
  <!-- Warning path -->
</elseif>
<else>
  <!-- Default path -->
</else>

<!-- Complex conditions -->
<if condition="(user_level == 'beginner' and error_type == 'syntax') or needs_help">
  <!-- Detailed guidance -->
</if>
```

### Loops and Iteration
```xml
<!-- Iterate over collections -->
<foreach items="package_list" as="package">
  Process {{ package.name }}
  Version: {{ package.version }}
</foreach>

<!-- Conditional iteration -->
<foreach items="errors" as="error">
  <if condition="error.severity == 'high'">
    Priority fix: {{ error.description }}
  </if>
</foreach>
```

### Error Handling
```xml
<error-handling>
  <!-- Specific error types -->
  <on-error type="parse_failure">
    Specific recovery action
  </on-error>

  <!-- Generic fallback -->
  <on-error type="unknown">
    Generic recovery with diagnostic info
  </on-error>

  <!-- Timeout handling -->
  <on-error type="timeout">
    Return partial results with status
  </on-error>
</error-handling>
```

## 🔒 Security Considerations

### Never Include
- ❌ Passwords or secrets in templates
- ❌ Personal identifying information
- ❌ System paths with usernames
- ❌ API keys or tokens
- ❌ Network addresses/IPs

### Always Sanitize
- ✅ User input before processing
- ✅ File paths to prevent traversal
- ✅ Command strings to prevent injection
- ✅ URLs to prevent SSRF

### Safe Patterns
```xml
<!-- Sanitize user input -->
<let name="safe_input">{{ user_input | sanitize }}</let>

<!-- Validate before use -->
<if condition="is_valid_path(file_path)">
  Process {{ file_path }}
</if>

<!-- Escape for shell commands -->
<let name="safe_cmd">{{ command | shell_escape }}</let>
```

## 🧪 Testing Templates

### Unit Testing Structure
```xml
<!-- test_template_name.poml -->
<test-suite>
  <test name="handles_normal_input">
    <input>
      <variable name="user_query">install firefox</variable>
    </input>
    <expected>
      <contains>pkgs.firefox</contains>
      <type>json</type>
    </expected>
  </test>

  <test name="handles_edge_case">
    <input>
      <variable name="user_query"></variable>
    </input>
    <expected>
      <error>missing_input</error>
    </expected>
  </test>
</test-suite>
```

### Validation Checklist
- [ ] All required variables defined
- [ ] Default values provided for optional variables
- [ ] Examples cover main use cases
- [ ] Error handling for common failures
- [ ] Output format clearly specified
- [ ] No security vulnerabilities
- [ ] Model hints appropriate for task
- [ ] Cache settings reasonable

## 📊 Performance Guidelines

### Caching Strategy
```xml
<!-- Cache deterministic queries -->
<cache duration="3600" key="query_hash" />

<!-- Don't cache personalized responses -->
<cache enabled="false" />

<!-- Cache with invalidation -->
<cache duration="1800" invalidate-on="config_change" />
```

### Token Optimization
1. **Be concise** in system prompts
2. **Limit examples** to 2-3 most representative
3. **Use references** instead of inline large contexts
4. **Set reasonable max_tokens** based on expected output

### Model Selection
```xml
<model-hints>
  <!-- Fast, simple tasks -->
  <preferred-models>gpt-3.5-turbo, mistral-7b</preferred-models>

  <!-- Complex reasoning -->
  <preferred-models>gpt-4, claude-3, llama-70b</preferred-models>

  <!-- Code generation -->
  <preferred-models>gpt-4, codellama-34b, starcoder</preferred-models>
</model-hints>
```

## 🔄 Orchestration Patterns

### Sequential Workflow
```xml
<workflow type="sequential">
  <step id="analyze">...</step>
  <step id="process" depends-on="analyze">...</step>
  <step id="validate" depends-on="process">...</step>
</workflow>
```

### Parallel Execution
```xml
<parallel>
  <agent id="checker1">...</agent>
  <agent id="checker2">...</agent>
  <agent id="checker3">...</agent>
</parallel>
```

### Conditional Branching
```xml
<workflow>
  <step id="classify">...</step>
  <branch on="classification_result">
    <case value="type_a">
      <step id="process_a">...</step>
    </case>
    <case value="type_b">
      <step id="process_b">...</step>
    </case>
    <default>
      <step id="process_default">...</step>
    </default>
  </branch>
</workflow>
```

## 📚 Documentation Requirements

### Template Documentation
Each template MUST include:
1. **Clear title and description** in metadata
2. **Variable documentation** via comments
3. **2-3 examples** showing typical usage
4. **Error handling** for common failures
5. **Output format specification**

### Inline Comments
```xml
<!-- Explain complex logic -->
<if condition="complex_condition">
  <!-- This handles the edge case where... -->
  Special processing
</if>

<!-- Document variable purpose -->
<let name="threshold">{{ threshold | default: 0.8 }}</let>
<!-- Threshold for similarity matching (0.0-1.0) -->
```

## ✅ Review Checklist

Before committing a POML template:

- [ ] **Metadata** complete with version
- [ ] **Variables** have defaults where appropriate
- [ ] **Examples** demonstrate main use cases
- [ ] **Error handling** covers failure modes
- [ ] **Output format** clearly specified
- [ ] **No security issues** (secrets, PII, etc.)
- [ ] **Tests** written for template
- [ ] **Documentation** explains usage
- [ ] **Style** follows this guide
- [ ] **Performance** considered (caching, tokens)

## 🚀 Advanced Features

### Dynamic Template Loading
```xml
<include template="{{ template_name }}.poml" />
```

### Template Inheritance
```xml
<extends template="base_analysis.poml">
  <override step="analyze">
    <!-- Specialized analysis -->
  </override>
</extends>
```

### Custom Functions
```xml
<functions>
  <function name="normalize_package_name">
    <param name="input" />
    <body>
      return input.toLowerCase().replace('-', '_')
    </body>
  </function>
</functions>
```

## 📖 References

- [Microsoft POML Specification](https://github.com/microsoft/poml)
- [POML v2.0 Schema](validators/schema.xsd)
- [Luminous Nix POML Examples](examples/)

---

*Last Updated: 2025-09-05*
*Version: 1.0.0*
