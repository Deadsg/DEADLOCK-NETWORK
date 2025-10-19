#!/bin/bash

echo "Documenting Nix flake assumptions for dream2nix and pip2nix"

# Get flake input paths
DREAM2NIX_PATH=$(nix eval --raw --extra-experimental-features nix-command flakes --expr '(builtins.getFlake ".").inputs.dream2nix.outPath')
PIP2NIX_PATH=$(nix eval --raw --extra-experimental-features nix-command flakes --expr '(builtins.getFlake ".").inputs.pip2nix.outPath')

echo "\n--- dream2nix assumptions ---"
echo "1. dream2nix.modules.dream2nix.pip is a module that can be directly imported and configured with project.name, project.src, and project.python.requirements."
echo "   Verification: Attempting to evaluate dream2nix.modules.dream2nix.pip as a module."
nix eval --raw --extra-experimental-features nix-command flakes \
  --expr 'with (import "${DREAM2NIX_PATH}"); dream2nix.modules.dream2nix.pip'

echo "\n--- pip2nix assumptions ---"
echo "1. pip2nix is a function that takes python and requirements as arguments."
echo "   Verification: Attempting to evaluate pip2nix as a function."
nix eval --raw --extra-experimental-features nix-command flakes \
  --expr 'with (import "${PIP2NIX_PATH}"); pip2nix'
