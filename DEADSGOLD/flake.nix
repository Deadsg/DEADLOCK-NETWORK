{
  description = "Deadsgold Python Shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }: let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };

    mySolders = pkgs.python3Packages.buildPythonPackage rec {
      pname = "solders";
      version = "0.19.0"; # Update to actual latest if needed

      src = pkgs.fetchPypi {
        inherit pname version;
        hash = "sha256-8403f59b0b49b8db1875ea383c58f249"; # Replace with real hash from PyPI
      };

      doCheck = false;
      # pythonImportsCheck = [ "solders" ];
    };
  in {
    devShells.${system}.default = pkgs.mkShell {
      name = "deadsgold";

      buildInputs = [
        (pkgs.python3.withPackages (ps: with ps; [
          flask
          requests
          numpy
          tkinter
          cryptography
          base58
        ]))
        pkgs.git
        mySolders
      ];

      shellHook = ''
        echo "💀 Welcome to the Deadsgold dev environment"
      '';
    };
  };
}
