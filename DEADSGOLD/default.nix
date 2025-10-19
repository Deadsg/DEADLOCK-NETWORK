
{
  pkgs ? import <nixpkgs> {},
  solana-py-src ? pkgs.fetchFromGitHub {
    owner = "michaelhly";
    repo = "solana-py";
    rev = "0726e04797f86a18373979dfca1dae24f928c0ff";
    sha256 = "0symcjk7633711072698kbfmix5c1mqjhhaxsg2pygxaydk2zjzj";
  },
  solders-src ? pkgs.fetchFromGitHub {
    owner = "kevinheavey";
    repo = "solders";
    rev = "2a00a7b57766f6a22a8849989d5c5ad40bf0a363";
    sha256 = "0wx47w86lcwm09d4ivz286hqkfq3bqw3wy75vz8afba0qbr4aw52";
  },
  jsonalias-src ? pkgs.fetchFromGitHub {
    owner = "kevinheavey";
    repo = "jsonalias";
    rev = "2a98db9c4024b1914f198f088f2aaa15a8cd7423";
    sha256 = "0a00zbx9cvjbfp0bggjavh7pidfhaahsz51zvyprh097kibg9xnl";
  }
}:

let
  jsonalias = pkgs.python3.pkgs.buildPythonPackage rec {
    pname = "jsonalias";
    version = "0.1.1";
    src = jsonalias-src;
    pyproject = true;
    build-system = [ pkgs.python3.pkgs.poetry-core ];
  };

  solders = pkgs.callPackage ./nix/solders { inherit jsonalias solders-src; };

  solana-py = pkgs.python3.pkgs.buildPythonPackage rec {
    pname = "solana-py";
    version = "0.1.0";
    src = solana-py-src;
    propagatedBuildInputs = [ solders ];
    pyproject = true;
    build-system = [ pkgs.python3.pkgs.poetry-core ];
  };

  python = pkgs.python3.withPackages (ps: with ps; [
    cryptography
    onnxruntime
    jsonalias
    solders
    solana-py
  ]);
in
pkgs.mkShell {
  buildInputs = [ python ];
}
