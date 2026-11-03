import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

load_dotenv()

from backend.database import engine, Base, BASE_DIR
from backend.routers import auth_routes, document_routes, contact_routes

# Create database tables automatically
Base.metadata.create_all(bind=engine)

def seed_default_users():
    try:
        from backend.database import SessionLocal
        from backend.models import User
        from backend.auth import hash_password
        db = SessionLocal()
        if db.query(User).count() == 0:
            db.add(User(
                email="admin@docuflow.ai",
                password_hash=hash_password("123456"),
                full_name="Quản trị viên DocuFlow",
                credits=999,
                role="admin"
            ))
            db.add(User(
                email="demo@gmail.com",
                password_hash=hash_password("123456"),
                full_name="Người dùng Demo",
                credits=100,
                role="user"
            ))
            db.commit()
            print("Đã tự động khởi tạo tài khoản demo: admin@docuflow.ai / 123456")
        db.close()
    except Exception as e:
        print("Notice seeding:", e)

seed_default_users()

app = FastAPI(
    title="DocuFlow AI API",
    description="Backend hệ thống trích xuất hóa đơn & tài liệu sang Excel bằng AI - Dự án EXE101",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_routes.router)
app.include_router(document_routes.router)
app.include_router(contact_routes.router)

# Mount uploads & assets directory
upload_dir = os.path.join(BASE_DIR, "uploads")
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

assets_dir = os.path.join(BASE_DIR, "assets")
os.makedirs(assets_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

image_dir = os.path.join(BASE_DIR, "Image")
os.makedirs(image_dir, exist_ok=True)
app.mount("/Image", StaticFiles(directory=image_dir), name="Image")

# Health Check Endpoint
@app.get("/api/health")
def health_check():
    gemini_ready = bool(os.getenv("GEMINI_API_KEY", "").strip())
    return {
        "status": "healthy",
        "service": "DocuFlow AI Backend",
        "database": "SQLite (docuflow.db)",
        "gemini_ai_configured": gemini_ready
    }

@app.get("/favicon.ico")
def get_favicon():
    fav_path = os.path.join(BASE_DIR, "favicon.ico")
    if os.path.exists(fav_path):
        return FileResponse(fav_path)
    return JSONResponse(status_code=404, content={"message": "Favicon not found"})

# Frontend Route Handlers
@app.get("/")
def read_root():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/index.html")
def read_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/app")
@app.get("/workspace")
@app.get("/docuflow_ai_web_application.html")
def read_workspace():
    return FileResponse(os.path.join(BASE_DIR, "docuflow_ai_web_application.html"))

@app.get("/login")
@app.get("/login.html")
def read_login():
    return FileResponse(os.path.join(BASE_DIR, "login.html"))

@app.get("/cach-thuc-hoat-dong.html")
def read_how_it_works():
    return FileResponse(os.path.join(BASE_DIR, "cach-thuc-hoat-dong.html"))

@app.get("/ve-chung-toi.html")
def read_about():
    return FileResponse(os.path.join(BASE_DIR, "ve-chung-toi.html"))

@app.get("/bang-gia.html")
def read_pricing():
    return FileResponse(os.path.join(BASE_DIR, "bang-gia.html"))

@app.get("/faq.html")
def read_faq():
    return FileResponse(os.path.join(BASE_DIR, "faq.html"))

if __name__ == "__main__":
    import uvicorn
    import sys
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    port = int(os.getenv("PORT", 8000))
    print("==================================================")
    print("DocuFlow AI Backend & Web Server is running!")
    print(f"Trang chu:        http://localhost:{port}")
    print(f"Ung dung/App:     http://localhost:{port}/app")
    print(f"Dang nhap:        http://localhost:{port}/login")
    print(f"Swagger API Docs: http://localhost:{port}/docs")
    print("==================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
