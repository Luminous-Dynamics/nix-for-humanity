{ lib
, python3
, fetchFromGitHub
, makeWrapper
}:

python3.pkgs.buildPythonApplication rec {
  pname = "luminous-nix";
  version = "0.3.0";

  src = fetchFromGitHub {
    owner = "Luminous-Dynamics";
    repo = "luminous-nix";
    rev = "v${version}";
    hash = "sha256-PLACEHOLDER"; # Update with actual hash after first build
  };

  format = "pyproject";

  nativeBuildInputs = with python3.pkgs; [
    poetry-core
    makeWrapper
  ];

  propagatedBuildInputs = with python3.pkgs; [
    # Core dependencies
    click
    rich
    prompt-toolkit
    pyyaml
    toml
    textual
    httpx
    questionary

    # Optional but recommended
    torch
    torchvision
    transformers

    # For caching
    sqlalchemy

    # For visualization
    plotly
    pandas
  ];

  # Optional dependencies
  passthru.optional-dependencies = with python3.pkgs; {
    neural = [ torch torchvision transformers ];
    voice = [ whisper pyttsx3 ];
    dev = [ pytest black ruff mypy ];
  };

  # Prevent tests from running during build (they require network)
  doCheck = false;

  postInstall = ''
    # Install model files
    mkdir -p $out/share/luminous-nix/models
    cp -r models/* $out/share/luminous-nix/models/ 2>/dev/null || true

    # Install configuration templates
    mkdir -p $out/share/luminous-nix/config
    cp -r config/* $out/share/luminous-nix/config/ 2>/dev/null || true

    # Wrap the executables to include model path
    wrapProgram $out/bin/luminous-nix \
      --set LUMINOUS_NIX_MODEL_PATH "$out/share/luminous-nix/models" \
      --set LUMINOUS_NIX_CONFIG_PATH "$out/share/luminous-nix/config"

    wrapProgram $out/bin/ask-nix \
      --set LUMINOUS_NIX_MODEL_PATH "$out/share/luminous-nix/models" \
      --set LUMINOUS_NIX_CONFIG_PATH "$out/share/luminous-nix/config"

    # Create convenience symlinks
    ln -s $out/bin/luminous-nix $out/bin/lnix
    ln -s $out/bin/ask-nix $out/bin/anix
  '';

  meta = with lib; {
    description = "Natural language interface for NixOS with 96% accuracy through neural networks";
    longDescription = ''
      Luminous Nix transforms NixOS system management by allowing users to
      interact with their system using natural language. With 96.3% accuracy
      achieved through advanced neural networks and active learning, it makes
      NixOS accessible to everyone.

      Features:
      - Natural language queries like "install firefox" or "update system"
      - 96.3% accuracy with continuous improvement
      - Sub-millisecond response times with intelligent caching
      - Active learning from user interactions
      - Support for development environments, package management, and system configuration
    '';
    homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
    changelog = "https://github.com/Luminous-Dynamics/luminous-nix/blob/v${version}/CHANGELOG.md";
    license = licenses.mit;
    maintainers = with maintainers; [ /* Add maintainer here */ ];
    platforms = platforms.linux;
    mainProgram = "luminous-nix";
  };
}
