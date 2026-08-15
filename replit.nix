# replit.nix - Gói hệ thống cho Nix
{ pkgs }: {
    deps = [
        pkgs.python38Full
        pkgs.python38Packages.pip
        pkgs.python38Packages.flask
        pkgs.python38Packages.flask-socketio
        pkgs.python38Packages.eventlet
        pkgs.openssh
        pkgs.curl
        pkgs.glibc
        pkgs.libxcrypt
        pkgs.nodejs  # cần để chạy npm install cho xterm nếu dùng, nhưng ta dùng CDN
    ];
    env = {
        LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
            pkgs.openssl
            pkgs.libxcrypt
        ];
    };
}
