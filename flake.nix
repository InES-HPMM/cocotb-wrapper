{
  description = "A wrapper around cocotb that facilitates using cocotb";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    treefmt-nix.url = "github:numtide/treefmt-nix";
    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs = {
        pyproject-nix.follows = "pyproject-nix";
        nixpkgs.follows = "nixpkgs";
      };
    };
    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs = {
        pyproject-nix.follows = "pyproject-nix";
        uv2nix.follows = "uv2nix";
        nixpkgs.follows = "nixpkgs";
      };
    };
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
    pyproject-nix,
    treefmt-nix,
    uv2nix,
    pyproject-build-systems,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (system: let
      pkgs = (import nixpkgs) {
        inherit system;
      };
      inherit (pkgs) lib;
      treefmt = treefmt-nix.lib.evalModule pkgs ./treefmt.nix;
    in {
      checks = {
        formatting = treefmt.config.build.check self;
      };
      formatter = treefmt.config.build.wrapper;
      packages = let
        workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};
        overlay = workspace.mkPyprojectOverlay {
          sourcePreference = "wheel";
        };
        pythonSet =
          (pkgs.callPackage pyproject-nix.build.packages {
            python = pkgs.python3;
          })
          .overrideScope
          (
            lib.composeManyExtensions [
              pyproject-build-systems.overlays.default
              overlay
            ]
          );
      in {
        default = pythonSet.mkVirtualEnv "cocotb-wrapper" workspace.deps.default;
      };
      devShells = {
        default = pkgs.mkShell {
          name = "cocotb-wrapper";
          packages = with pkgs; [
            just
            nodePackages.prettier
            python3
            python3Packages.uv
          ];
          env =
            {
              UV_PYTHON_DOWNLOADS = "never";
              UV_PYTHON = pkgs.python3.interpreter;
            }
            // lib.optionalAttrs pkgs.stdenv.isLinux {
              LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.pythonManylinuxPackages.manylinux1;
            };
          shellHook = ''
            unset PYTHONPATH
          '';
        };
      };
    });
}
