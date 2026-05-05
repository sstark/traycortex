{ lib, pkgs,... }:
let
    traycortex = pkgs.python3Packages.buildPythonApplication {
        pname = "traycortex";
        version = "0.5.2";
        format = "pyproject";

        build-system = with pkgs; [
            python3Packages.uv
            python3Packages.uv-build
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

        src = pkgs.fetchFromGitHub {
            owner = "sstark";
            repo = "traycortex";
            rev = "c2c2b78956be97d3513198766f28bc40bee31a67";
            hash = "sha256-duvFWGqS3VLDORMoZgpqOFFtht72Dt/WH3nKOPBv/+U=";
        };

        meta = {
            homepage = "https://github.com/sstark/traycortex";
            description = "Tray application to monitor the status of borgmatic backups";
            license = lib.licenses.gpl3;
        };

        preFixup = ''
            makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
        '';
    };
in
{
    home.packages = [
        pkgs.libayatana-indicator
        traycortex
    ];
}
