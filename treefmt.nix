{
  projectRootFile = "flake.nix";
  programs = {
    alejandra.enable = true;
    prettier.enable = true;
    ruff-format.enable = true;
  };
  settings.global.excludes = [
    ".cache/**"
    ".direnv/**"
    ".env/**"
    ".git/**"
    ".jj/**"
    ".venv/**"
    ".ruff_cache/**"
    ".svn/**"
    "build/**"
  ];
}
