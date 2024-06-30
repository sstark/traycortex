
# Traycortex

traycortex is an application that will show the status of [borgmatic
backup](https://torsion.org/borgmatic/) in your system tray. It will also let
you trigger backups from the menu.

Features:

  - System **tray menu** for running borgmatic
  - Client application to **integrate with borgmatic** for detecting timed backup runs
  - **Notifications** (backup started, backup finished)
  - Configuration file to allow customizing the borgmatic command
  - **ssh-agent detection** to enable easy use of password protected ssh keys

Along with it comes a *traycortex-cli* application, that is used in the
borgmatic hooks configuration to signal the tray icon. Possible states are
`job_started`, `job_finished` and `job_error`.

![screenshot of tray running](doc/tray-running.png)

When the status of a backup is updated, a notification will be displayed and the
icon changes accordingly.


## Installation

### Prerequites

Some packages are required to build and install traycortex (probably incomplete):

  - Ubuntu: `apt install libcairo2-dev python-gi-dev libgirepository1.0-dev`
  - Arch: `pacman -S gobject-introspection python-cairo libappindicator-gtk3`

Recommended way to install:

    pipx install traycortex

Also works:

    pip install traycortex

*Packagers welcome*


### Configuration File

Location: `$XDG_CONFIG_HOME/traycortex.ini`

To create a working minimal configuration (if you do not have one already) use:

    traycortex-cli --ini

This will generate a random authkey and place it in a new configuration file.
If a configuration file already exists, above command will fail.

### Configuration File Options

The authentication key and port for the connection between traycortex and
traycortex-cli:

    [connection]
    ; no default value. Randomly set on "traycortex-cli --ini".
    authkey = ce03f7af891ebc29defc0643faf71025
    ; default:
    ;   port = 35234
    port = 54321

The command used to create a backup (when selecting the "Engage" menu item):

    [borgmatic]
    ; default:
    ;   command = borgmatic
    ; For testing non-interactive ssh you can set this:
    ;   command = ssh -oBatchMode=yes <backupserver> date
    command = systemd-inhibit --why="Backup is running" /usr/local/bin/borgmatic


## Running

To start the tray application from the command line:

    traycortex &

Or create a desktop file `~/.local/share/applications/traycortex.desktop`:

    [Desktop Entry]
    Exec=traycortex
    ; For the icon to work you need to place borgmatic.png in `~/.icons`
    Icon=borgmatic
    Name=traycortex
    Type=Application

Now you can start traycortex with your usual desktop method.


## Tray Menu

  - **Engage**: Run a borgmatic backup
  - **Discard**: Quit traycortex and remove the icon from the tray. If a backup
    is currently running, it will be killed.


## Integrating with borgmatic

Example `~/.config/borgmatic.d/home.yaml`:

    [...]
    source_directories:
        - /home/seb
    repositories:
        - path: ssh://...
    before_backup:
        - traycortex-cli job_started
    after_check:
        - traycortex-cli job_finished
    on_error:
        - traycortex-cli job_error
    [...]


## ssh-agent detection

With borgmatic it is likely you use ssh to access a remote backup repository.
You probably have public key authentication set up for this to allow
non-interactive use. And probably you also want to have a passphrase set
for the private ssh key.

traycortex will try to detect a running ssh-agent and set the environment for
borgmatic to have the `SSH_AUTH_SOCK` environment variable set. This makes it
independent from its starting environment with regard to that variable.

You will still have to add your key to the running ssh-agent.

It is recommended to use

    ssh_command: ssh -oBatchMode=yes

in your borgmatic configuration. This way, if ssh-agent detection fails, or you
have not added the necessary key to it, borgmatic will properly fail and not
wait for input in the background.

If you have multiple ssh-agents running, traycortex currently has no way to
know which one is correct and will simply use the first one found.
