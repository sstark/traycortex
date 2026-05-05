{ lib, pkgs, ... }:
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
            rev = "f43c820f976d37a9f16682b673e6dce00c3199b1";
            hash = "sha256-QjhKhhvrt/6hB7zpm1CMLPQcwWZ8g79Z7MFyBUpD/Qg=";
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
