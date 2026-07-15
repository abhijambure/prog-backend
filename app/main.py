from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, student, career, assessment, chat, admin

# Setup FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Career Compass AI - An AI-powered Career Guidance Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(career.router)
app.include_router(assessment.router)
app.include_router(chat.router)
app.include_router(admin.router)

@app.on_event("startup")
def startup_event():
    # Attempt to create tables if they do not exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized successfully.")
    except Exception as e:
        print(f"Error during database initialization: {e}")

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "docs_url": "/docs",
        "status": "healthy"
    }
