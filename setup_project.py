import os
import json
import shutil
from pathlib import Path

def create_file(path, content):
    """יצירת קובץ עם התוכן שלו"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def setup_project():
    # יצירת תיקיית הפרויקט
    project_name = "ocr-forms"
    base_dir = Path(project_name)
    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir()

    # יצירת תיקיות
    directories = [
        base_dir / "backend/app/processors",
        base_dir / "backend/app/models",
        base_dir / "backend/app/utils",
        base_dir / "backend/storage/uploads",
        base_dir / "backend/storage/processed",
        base_dir / "backend/storage/history",
        base_dir / "frontend/public",
        base_dir / "frontend/src/components/FileUpload",
        base_dir / "frontend/src/components/ui",
        base_dir / "frontend/src/services",
        base_dir / "frontend/src/styles"
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

    # קבצי Backend
    backend_files = {
        base_dir / "backend/requirements.txt": """fastapi==0.109.2
uvicorn==0.27.1
python-multipart==0.0.9
Pillow==10.2.0
pytesseract==0.3.10
numpy==1.26.4
python-jose==3.3.0
passlib==1.7.4
python-dotenv==1.0.0
PyMuPDF==1.23.8""",

        base_dir / "backend/app/main.py": """import os
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import logging
from app.processors.document_processor import DocumentProcessor
from app.utils.file_handlers import save_upload_file

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# הפעלת האפליקציה
app = FastAPI(title="OCR Forms API")

# הגדרת CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# הגדרת משתני סביבה
PORT = int(os.getenv("PORT", 8000))

STORAGE_PATH = Path("storage")
UPLOAD_PATH = STORAGE_PATH / "uploads"
PROCESSED_PATH = STORAGE_PATH / "processed"

for path in [UPLOAD_PATH, PROCESSED_PATH]:
    path.mkdir(parents=True, exist_ok=True)

processor = DocumentProcessor()

@app.post("/api/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = save_upload_file(file, UPLOAD_PATH)
        result = await processor.process_file(file_path)
        return result
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "OCR Forms API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
""",

        base_dir / "backend/Dockerfile": """FROM python:3.11-slim

RUN apt-get update && apt-get install -y \\
    tesseract-ocr \\
    tesseract-ocr-heb \\
    libgl1-mesa-glx \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "${PORT:-8000}"]
""",

        base_dir / "docker-compose.yml": """version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - PORT=8000
    restart: unless-stopped
    
  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
    restart: unless-stopped
"""
    }

    # יצירת קבצי Backend
    for file_path, content in backend_files.items():
        create_file(file_path, content)

    # יצירת package.json ל-Frontend
    package_json = {
        "name": "ocr-forms-frontend",
        "private": True,
        "version": "0.1.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "react-router-dom": "^6.22.1",
            "lucide-react": "^0.363.0",
            "@radix-ui/react-dialog": "^1.0.5",
            "@radix-ui/react-alert-dialog": "^1.0.5",
            "tailwindcss": "^3.4.1",
            "axios": "^1.6.7"
        },
        "devDependencies": {
            "@types/react": "^18.2.64",
            "@types/react-dom": "^18.2.21",
            "@vitejs/plugin-react": "^4.2.1",
            "autoprefixer": "^10.4.18",
            "postcss": "^8.4.35",
            "vite": "^5.1.6"
        }
    }
    create_file(base_dir / "frontend/package.json", json.dumps(package_json, indent=2))

    print("Project setup completed successfully!")
    print("\nTo start the project:")
    print("1. cd ocr-forms")
    print("2. Run: docker-compose up --build")
    print("\nOr for local development:")
    print("\nBackend:")
    print("1. cd backend")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # or 'venv\\Scripts\\activate' on Windows")
    print("4. pip install -r requirements.txt")
    print("5. uvicorn app.main:app --reload")
    print("\nFrontend:")
    print("1. cd frontend")
    print("2. npm install")
    print("3. npm run dev")

if __name__ == "__main__":
    setup_project()
