{ pkgs }: {
    deps = [
        pkgs.python310Full
        pkgs.python310Packages.pip
        pkgs.python310Packages.flask
        pkgs.python310Packages.paramiko
        pkgs.python310Packages.flask-socketio
        pkgs.python310Packages.eventlet
        pkgs.openssh
        pkgs.curl
        pkgs.glibc
        pkgs.libxcrypt
        pkgs.nodejs
    ];
    env = {
        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.openssl
            pkgs.libxcrypt
        ];
    };
}
