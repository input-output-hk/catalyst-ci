{
  inputs,
  cell,
}: let
  inherit (inputs) nixpkgs std;
  l = nixpkgs.lib // builtins;
in {
  conform = std.std.nixago.conform {
    configData = {
      commit = {
        header = {length = 89;};
        conventional = {
          types = [
            "build"
            "chore"
            "ci"
            "docs"
            "feat"
            "fix"
            "perf"
            "refactor"
            "style"
            "test"
            "wip"
          ];
          scopes = [];
        };
      };
    };
  };
  lefthook = std.std.nixago.lefthook {
    configData = {
      commit-msg = {
        commands = {
          conform = {
            run = "${nixpkgs.conform}/bin/conform enforce --commit-msg-file {1}";
          };
        };
      };
      pre-commit = {
        commands = {
          treefmt = {
            run = "${nixpkgs.treefmt}/bin/treefmt --fail-on-change {staged_files}";
          };
          golint = {
            run = "golint {staged_files}";
            glob = "*.go";
          };
          govet = {
            run = "cd cli && go vet ./...";
            glob = "*.go";
          };
        };
      };
    };
  };
  prettier =
    std.lib.dev.mkNixago
    {
      configData = {
        printWidth = 80;
        proseWrap = "always";
      };
      output = ".prettierrc";
      format = "json";
      packages = with nixpkgs; [nodePackages.prettier];
    };
  treefmt =
    std.std.nixago.treefmt
    {
      configData = {
        formatter = {
          go = {
            command = "golines";
            includes = ["*.go"];
            options = [
              "-m"
              "80"
              "--reformat-tags"
              "-w"
            ];
          };
          nix = {
            command = "alejandra";
            includes = ["*.nix"];
          };
          prettier = {
            command = "prettier";
            options = ["--write"];
            includes = [
              "*.md"
            ];
          };
        };
      };
      packages = with nixpkgs; [alejandra];
    };
}
