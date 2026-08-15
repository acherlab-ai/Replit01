# 
#!/bin/bash
echo "==> Cài đặt dependencies Python"
pip3 install -r requirements.txt --quiet

echo "==> Khởi động Flask + SocketIO trên cổng 8080"
python3 app.py
