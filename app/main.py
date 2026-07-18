from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, student, career, assessment, chat, admin
import logging
from fastapi import Request
from fastapi.responses import JSONResponse

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

logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup_event():
    # Attempt to create tables if they do not exist
    try:
        from app.core.database import engine, Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.exception("Database initialization failed")

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/")
def read_root():
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "docs_url": "/docs",
        "status": "healthy"
    }

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "healthy"}
