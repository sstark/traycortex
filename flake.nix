{
  description = "Tray application to monitor the status of borgmatic backups";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;
      systems = [ "x86_64-linux" "aarch64-linux" ];
      forAllSystems = lib.genAttrs systems;

      src = lib.fileset.toSource {
        root = ./.;
        fileset = lib.fileset.unions [
          ./pyproject.toml
          ./README.md
          ./LICENSE
          ./traycortex
        ];
      };

      mkTraycortex = pkgs: pkgs.python3Packages.buildPythonApplication {
        pname = "traycortex";
        version = "0.5.2";
        pyproject = true;

        inherit src;

        build-system = with pkgs.python3Packages; [
          uv
          uv-build
        ];

        nativeBuildInputs = with pkgs; [
          wrapGAppsHook3
          gobject-introspection
        ];

        propagatedBuildInputs = with pkgs.python3Packages; [
          pygobject3
          pystray
          pillow
          platformdirs
        ];

        preFixup = ''
          makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
        '';

        meta = {
          homepage = "https://github.com/sstark/traycortex";
          description = "Tray application to monitor the status of borgmatic backups";
          license = lib.licenses.gpl3Only;
          mainProgram = "traycortex";
          platforms = systems;
        };
      };
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          traycortex = mkTraycortex pkgs;
        in
        {
          inherit traycortex;
          default = traycortex;
        });

      apps = forAllSystems (system: {
        default = {
          type = "app";
          program = lib.getExe self.packages.${system}.default;
        };
      });

      homeModules.default = { config, lib, pkgs, ... }:
        let
          cfg = config.services.traycortex;
        in
        {
          options.services.traycortex = {
            enable = lib.mkEnableOption
              "the traycortex tray icon for monitoring borgmatic backups";

            package = lib.mkOption {
              type = lib.types.package;
              default = mkTraycortex pkgs;
              defaultText = lib.literalExpression
                "traycortex.packages.\${pkgs.system}.default";
              description = "The traycortex package to use.";
            };

            useSystemd = lib.mkOption {
              type = lib.types.bool;
              default = true;
              description = ''
                Whether to run traycortex as a systemd user service tied to
                graphical-session.target. When false, traycortex is only
                installed to home.packages and you have to start it yourself
                (e.g. via your desktop autostart).
              '';
            };
          };

          config = lib.mkMerge [
            (lib.mkIf cfg.enable {
              home.packages = [
                pkgs.libayatana-indicator
                cfg.package
              ];
            })

            (lib.mkIf (cfg.enable && cfg.useSystemd) {
              systemd.user.services.traycortex = {
                Unit = {
                  Description =
                    "Tray application to monitor the status of borgmatic backups";
                  After = [ "graphical-session.target" ];
                  PartOf = [ "graphical-session.target" ];
                };

                Service = {
                  ExecStart = lib.getExe cfg.package;
                  Restart = "on-failure";
                  RestartSec = 3;
                };

                Install.WantedBy = [ "graphical-session.target" ];
              };
            })
          ];
        };
    };
}
