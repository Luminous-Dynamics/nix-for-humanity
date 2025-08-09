# Local LLM Configuration for Nix for Humanity
# Sacred Trinity Model Selection: Mistral-7B

{
  # Sacred Trinity default: Mistral-7B
  # Chosen for perfect balance of performance, accuracy, and accessibility
  # Users can override by setting NIX_GURU_MODEL environment variable
  
  models = {
    # SACRED TRINITY CHOICE - Best for NixOS expertise
    default = "mistral:7b";
    
    # Model options with Sacred Trinity recommendations
    
    # ⭐ PRIMARY CHOICE - Sacred Trinity Default
    balanced = {
      name = "mistral:7b";
      ram = "6GB minimum";
      description = "Sacred Trinity choice - Perfect balance for NixOS development";
      strengths = [
        "Excellent technical comprehension"
        "Fast response times (< 5 seconds)"
        "Strong NixOS pattern recognition"
        "Runs on modest hardware"
      ];
    };
    
    # Alternative models for different needs
    lightweight = {
      name = "phi:2.7b";
      ram = "3GB minimum";
      description = "Minimal model for very limited RAM";
      useCase = "Basic NixOS questions on older hardware";
    };
    
    code-focused = {
      name = "deepseek-coder:6.7b";
      ram = "8GB minimum";
      description = "Specialized for code generation";
      useCase = "Heavy Nix expression writing";
    };
    
    detailed = {
      name = "codellama:13b-instruct";
      ram = "16GB minimum";
      description = "More detailed technical explanations";
      useCase = "Complex NixOS debugging and learning";
    };
    
    advanced = {
      name = "mixtral:8x7b-instruct";
      ram = "32GB minimum";
      description = "Highest quality but resource intensive";
      useCase = "Research or when accuracy is critical";
    };
  };
  
  # Model selection logic
  selectModel = systemRam: 
    if systemRam < 4 then "phi:2.7b"
    else if systemRam < 8 then "mistral:7b"
    else if systemRam < 16 then "mistral:7b"  # Still best choice
    else if systemRam < 32 then "codellama:13b"
    else "mixtral:8x7b";
  
  # Prompt templates optimized for each model type
  prompts = {
    default = question: ''
      You are a NixOS expert assistant. Answer the following question concisely and accurately.
      Focus on practical solutions and best practices.
      
      Question: ${question}
      
      Answer:
    '';
    
    code = question: ''
      You are a NixOS development expert. Provide code examples and technical details.
      
      Question: ${question}
      
      Provide:
      1. Direct answer
      2. Code example if applicable
      3. Best practices
      
      Answer:
    '';
    
    beginner = question: ''
      You are a friendly NixOS helper. Explain in simple terms without jargon.
      
      Question: ${question}
      
      Explain simply:
    '';
  };
}