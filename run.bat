@echo off
chcp 65001 >nul
echo ===================================================
echo     DOCUFLOW AI - HỆ THỐNG TRÍCH XUẤT HÓA ĐƠN
echo ===================================================
echo Đang khởi động Backend FastAPI & Cơ sở dữ liệu SQLite...

if not exist .venv (
    echo Môi trường chưa khởi tạo, đang tạo .venv...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo ===================================================
echo 🌐 Trang chủ:        http://localhost:8000
echo 📊 Không gian Web:   http://localhost:8000/app
echo 🔑 Đăng nhập:        http://localhost:8000/login
echo 📖 API Docs:         http://localhost:8000/docs
echo ===================================================
echo.
start http://localhost:8000
python main.py
pause

