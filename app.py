# app.py - Web Terminal sử dụng xterm.js và SocketIO
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import subprocess
import threading
import os
import signal
import pty
import select
import termios
import tty

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Lưu trữ tiến trình shell cho mỗi phiên (dùng session id)
sessions = {}

def create_shell_session(sid):
    """Tạo một shell PTY cho phiên kết nối"""
    master, slave = pty.openpty()
    # Thiết lập terminal attributes
    old_settings = termios.tcgetattr(slave)
    tty.setraw(slave)
    # Khởi chạy bash trong PTY
    process = subprocess.Popen(
        ['/bin/bash', '-i'],
        stdin=slave,
        stdout=slave,
        stderr=slave,
        preexec_fn=os.setsid,
        close_fds=True
    )
    # Lưu thông tin
    sessions[sid] = {
        'master': master,
        'slave': slave,
        'process': process,
        'old_settings': old_settings,
        'pid': process.pid
    }
    # Luồng đọc output từ master và gửi về client
    def reader():
        while True:
            try:
                data = os.read(master, 1024)
                if not data:
                    break
                socketio.emit('output', data.decode('utf-8', errors='ignore'), room=sid)
            except OSError:
                break
        # Khi kết thúc, dọn dẹp
        cleanup_session(sid)

    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    return master

def cleanup_session(sid):
    if sid in sessions:
        sess = sessions[sid]
        try:
            os.close(sess['master'])
            os.close(sess['slave'])
            sess['process'].terminate()
            sess['process'].wait()
        except:
            pass
        del sessions[sid]

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    # Tạo shell cho phiên này
    create_shell_session(request.sid)
    emit('info', 'Terminal ready')

@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client disconnected: {request.sid}')
    cleanup_session(request.sid)

@socketio.on('input')
def handle_input(data):
    """Nhận dữ liệu từ xterm và ghi vào master PTY"""
    sid = request.sid
    if sid in sessions:
        master = sessions[sid]['master']
        try:
            os.write(master, data.encode())
        except OSError:
            pass  # Phiên đã đóng

@socketio.on('resize')
def handle_resize(data):
    """Thay đổi kích thước terminal (cols, rows)"""
    sid = request.sid
    if sid in sessions:
        master = sessions[sid]['master']
        cols = data.get('cols', 80)
        rows = data.get('rows', 24)
        try:
            # Điều chỉnh kích thước PTY
            import fcntl
            import struct
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(master, termios.TIOCSWINSZ, winsize)
        except:
            pass

@app.route('/')
def index():
    return render_template('terminal.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
