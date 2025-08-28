{ lib
, python3Packages
, fetchFromGitHub
}:

python3Packages.buildPythonPackage rec {
  pname = "luminous-nix";
  version = "0.3.2";
  
  src = ../.;
  
  propagatedBuildInputs = with python3Packages; [
    click
    pydantic
    rich
    pyyaml
    sqlalchemy
  ];
  
  checkInputs = with python3Packages; [
    pytest
    pytest-cov
    pytest-mock
  ];
  
  # Disable tests that require network or Nix
  checkPhase = ''
    pytest tests/unit
  '';
  
  meta = with lib; {
    description = "Natural language interface for NixOS";
    homepage = "https://github.com/Luminous-Dynamics/luminous-nix";
    license = licenses.mit;
    maintainers = [ ];
  };
}
