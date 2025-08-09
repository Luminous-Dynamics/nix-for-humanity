# Power User Model Configuration (16GB+ RAM)
# Strategic model selection for different development scenarios

{
  # Model selection strategy for systems with ample RAM
  powerUserStrategy = {
    
    # Quick Development Cycle (Default)
    rapid = {
      model = "mistral:7b";
      useCase = "Active coding with rapid Q&A";
      responseTime = "2-5 seconds";
      ramUsage = "~6GB";
      when = [
        "Writing code actively"
        "Quick syntax questions"
        "Common patterns"
        "Maintaining flow state"
      ];
      example = "ask-nix-guru 'How do I install a package?'";
    };
    
    # Deep Technical Work
    detailed = {
      model = "codellama:13b-instruct";
      useCase = "Complex problems requiring detailed explanations";
      responseTime = "5-10 seconds";
      ramUsage = "~13GB";
      when = [
        "Writing custom NixOS modules"
        "Debugging complex derivations"
        "Understanding Nix internals"
        "Learning new concepts"
        "Code review sessions"
      ];
      example = ''
        NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru \
          "Explain the difference between buildInputs and nativeBuildInputs with examples"
      '';
    };
    
    # Code Generation Focus
    coding = {
      model = "deepseek-coder:6.7b";
      useCase = "Specialized code generation";
      responseTime = "3-6 seconds";
      ramUsage = "~8GB";
      when = [
        "Writing complex Nix expressions"
        "Generating boilerplate"
        "Converting imperative to declarative"
        "Package definitions"
      ];
      example = ''
        NIX_GURU_MODEL=deepseek-coder:6.7b ask-nix-guru \
          "Generate a complete flake.nix for a Rust project"
      '';
    };
    
    # Maximum Quality (32GB+ RAM)
    research = {
      model = "mixtral:8x7b-instruct";
      useCase = "Highest quality responses when time permits";
      responseTime = "10-20 seconds";
      ramUsage = "~26GB";
      when = [
        "Research and exploration"
        "Architecture decisions"
        "Complex system design"
        "Teaching others"
      ];
      example = ''
        NIX_GURU_MODEL=mixtral:8x7b-instruct ask-nix-guru \
          "Design a NixOS configuration for a high-availability web service"
      '';
    };
  };
  
  # Recommended workflows by RAM
  workflowsByRam = {
    "16GB" = {
      primary = "mistral:7b";
      secondary = "codellama:13b-instruct";
      strategy = "Use Mistral for flow, CodeLlama for complexity";
    };
    
    "32GB" = {
      primary = "mistral:7b";
      secondary = "codellama:13b-instruct";
      tertiary = "mixtral:8x7b-instruct";
      strategy = "Mistral default, CodeLlama for depth, Mixtral for research";
    };
    
    "64GB+" = {
      primary = "codellama:13b-instruct";  # Can afford to use as default
      secondary = "mixtral:8x7b-instruct";
      strategy = "CodeLlama default for quality, Mixtral for complex work";
    };
  };
  
  # Shell aliases for power users
  shellAliases = {
    # Quick model switching
    "nix-guru-fast" = "NIX_GURU_MODEL=mistral:7b ask-nix-guru";
    "nix-guru-detail" = "NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru";
    "nix-guru-code" = "NIX_GURU_MODEL=deepseek-coder:6.7b ask-nix-guru";
    "nix-guru-best" = "NIX_GURU_MODEL=mixtral:8x7b-instruct ask-nix-guru";
    
    # Model management
    "nix-guru-models" = "ollama list";
    "nix-guru-pull" = "ollama pull";
  };
  
  # Parallel model usage (advanced)
  parallelQueries = ''
    # Run different models for comparison
    compare-models() {
      local question="$*"
      echo "🔄 Comparing model responses for: $question"
      echo
      
      echo "=== Mistral-7B (Fast) ==="
      time NIX_GURU_MODEL=mistral:7b ask-nix-guru "$question" | head -10
      echo
      
      echo "=== CodeLlama-13B (Detailed) ==="
      time NIX_GURU_MODEL=codellama:13b-instruct ask-nix-guru "$question" | head -10
      echo
    }
  '';
}