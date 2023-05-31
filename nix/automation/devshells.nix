{
  inputs,
  cell,
}: let
  inherit (inputs) nixpkgs std;
  l = nixpkgs.lib // builtins;

  mkEnv = env: l.mapAttrsToList (name: value: {inherit name value;}) env;

  # Common deps
  common = {...}: {
    imports = [
      std.std.devshellProfiles.default
    ];
    nixago = [
      cell.configs.conform
      cell.configs.lefthook
      cell.configs.prettier
      cell.configs.treefmt
    ];
    packages = with nixpkgs; [
      # Go
      delve
      gcc
      ginkgo
      go
      golines
      golint
      gopls
      go-tools
    ];
  };
in
  l.mapAttrs (_: std.lib.dev.mkShell) rec {
    default = {...}: {
      name = nixpkgs.lib.mkForce "Catalyst CI";
      imports = [
        common
      ];
    };
  }
