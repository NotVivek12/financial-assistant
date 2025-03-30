{
  description = "Financial Advisor Project";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
  let
    system = "x86_64-linux";
    pkgs = import nixpkgs { inherit system; };
  in
  {
    devShells.${system}.default = pkgs.mkShell {
      packages = with pkgs; [
        pkgs.python3
        pkgs.python3Packages.flask
        pkgs.python3Packages.google-generativeai
        pkgs.python3Packages.python-dotenv
      ];
    };
  };
}