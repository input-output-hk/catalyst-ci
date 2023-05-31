{
  description = "Cardano Catalyst World";
  inputs = {
    ## Nixpkgs ##
    nixpkgs.url = "github:nixos/nixpkgs/nixpkgs-unstable";

    ## Std ##
    std.url = "github:divnix/std/5384b5eec8780cbb1823b70d64b51449f65541b7";
    std.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = {std, ...} @ inputs:
    std.growOn
    {
      inherit inputs;
      cellsFrom = ./nix;

      cellBlocks = [
        (std.blockTypes.devshells "devshells" {ci.build = true;})
        (std.blockTypes.nixago "configs")
      ];
    }
    {
      devShells = std.harvest inputs.self ["automation" "devshells"];
    };

  nixConfig = {
    extra-substituters = [
      "https://cache.iog.io"
      "https://iog-catalyst-nix.s3.eu-central-1.amazonaws.com"
    ];
    extra-trusted-public-keys = [
      "hydra.iohk.io:f/Ea+s+dFdN+3Y/G+FDgSq+a5NEWhJGzdjvKNGv0/EQ="
      "catalyst:kNW0n7ijUJDvu4BrpqC3j54rgoHNccXx7ABuVzuL9WM="
    ];
    allow-import-from-derivation = "true";
  };
}
