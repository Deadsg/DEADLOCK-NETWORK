
{
  pkgs,
  solders-src,
  jsonalias,
}:

let
  solders-deps = pkgs.rustPlatform.fetchCargoVendor {
    src = solders-src;
    hash = "sha256-+8iaA1Cs+7qiDfQpwPAWSZ1HuF85WaDZB3MN57QOodI=";
  };
in
pkgs.rustPlatform.buildRustPackage rec {
  pname = "solders";
  version = "0.26.0";
  src = solders-src;
  cargoDeps = solders-deps;
  nativeBuildInputs = with pkgs; [ maturin rustc cargo ];
  propagatedBuildInputs = [ pkgs.python3.pkgs.typing-extensions jsonalias ];
}
