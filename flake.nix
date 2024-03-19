{
  description = "A wrapper around cocotb that facilitates using cocotb";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    poetry2nix = {
      url = "github:nix-community/poetry2nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = inputs@{ flake-parts, poetry2nix, ... }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      perSystem = { config, pkgs, ... }:
        let
          inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        in
        {
          formatter = pkgs.nixpkgs-fmt;
          packages = {
            cocotb-wrapper = mkPoetryApplication {
              projectDir = ./.;
              preferWheels = true;
            };
            default = config.packages.cocotb-wrapper;
          };
          devShells = {
            default = pkgs.mkShell {
              name = "cocotb-wrapper";
              packages = with pkgs; [ nodejs poetry poetryPlugins.poetry-plugin-export pre-commit ];
            };
          };
        };
    };
}
