
{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = with pkgs; [
    python3
    (python3.withPackages (ps: with ps; [
      cryptography
      onnxruntime
      solana
      anchorpy
      base58
    ]))
  ];

  shellHook = ''
    export PYTHONPATH="${pkgs.lib.makeSearchPath "lib/python3.12/site-packages" (with pkgs.python3.pkgs; [ cryptography onnxruntime solana anchorpy base58 ])}"
  '';
}
