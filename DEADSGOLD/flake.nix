{
  description = "Deadsgold Python Shell";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in {
    devShells.${system}.default = pkgs.mkShell {
      name = "deadsgold";

      buildInputs = [
        (pkgs.python3.withPackages (ps: with ps; [
          flask
          requests
          numpy
        ]))
        pkgs.git
      ];

      shellHook = ''
        echo "💀 Welcome to the Deadsgold dev environment"
      '';
    };
  };
}
