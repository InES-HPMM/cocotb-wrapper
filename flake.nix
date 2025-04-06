{
  description = "A wrapper around cocotb that facilitates using cocotb";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
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
    nixpkgs,
    uv2nix,
    pyproject-nix,
    pyproject-build-systems,
    ...
  }: let
    inherit (nixpkgs) lib;
    supportedSystems = ["x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin"];
    forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
    pkgs = forAllSystems (system: nixpkgs.legacyPackages.${system});
  in {
    formatter = forAllSystems (system: pkgs.${system}.alejandra);
    packages = forAllSystems (system: let
      workspace = uv2nix.lib.workspace.loadWorkspace {workspaceRoot = ./.;};
      overlay = workspace.mkPyprojectOverlay {
        sourcePreference = "wheel";
      };
      pythonSet =
        (pkgs.${system}.callPackage pyproject-nix.build.packages {
          python = pkgs.${system}.python3;
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
    });
    devShells = forAllSystems (system: {
      default = pkgs.${system}.mkShell {
        name = "cocotb-wrapper";
        packages = with pkgs.${system}; [
          just
          python3
          python3Packages.uv
        ];
        env =
          {
            UV_PYTHON_DOWNLOADS = "never";
            UV_PYTHON = pkgs.${system}.python3.interpreter;
          }
          // lib.optionalAttrs pkgs.${system}.stdenv.isLinux {
            LD_LIBRARY_PATH = lib.makeLibraryPath pkgs.${system}.pythonManylinuxPackages.manylinux1;
          };
        shellHook = ''
          unset PYTHONPATH
        '';
      };
    });
  };
}
