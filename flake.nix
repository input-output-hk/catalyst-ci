# cspell: words substituters cachix rrbutani
{
  description = "Catalyst CI";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devenv.url = "github:cachix/devenv";
    mk-shell-bin.url = "github:rrbutani/nix-mk-shell-bin";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = inputs @ {flake-parts, ...}:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [
        inputs.devenv.flakeModule
      ];
      systems = ["x86_64-linux" "i686-linux" "x86_64-darwin" "aarch64-linux" "aarch64-darwin"];

      perSystem = {
        config,
        self',
        inputs',
        pkgs,
        system,
        ...
      }: {
        devenv.shells.default = {
          name = "Catalyst CI";
          packages = with pkgs; [
            # Go
            delve
            gcc
            ginkgo
            go
            golines
            golint
            gopls
            go-tools

            # Node
            nodejs_20
            nodePackages.typescript

            # Python
            python312
          ];
          enterShell = ''
            echo "Welcome to the Catalyst CI development environment!"
          '';
        };
      };
    };
}
