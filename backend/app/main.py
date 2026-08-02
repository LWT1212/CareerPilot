from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.projects import router as projects_router
from app.api.v1.chats import router as chats_router, project_router, message_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.experiences import router as experiences_router
from app.api.v1.interviews import router as interviews_router, question_router
from app.api.v1.documents import router as documents_router
from app.api.v1.agents import router as agents_router
from app.db import init_db

app = FastAPI(
    title="CareerPilot AI",
    description="基于Multi-Agent的长期项目成长助手",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(chats_router, prefix="/api/v1")
app.include_router(project_router, prefix="/api/v1")
app.include_router(message_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(experiences_router, prefix="/api/v1")
app.include_router(interviews_router, prefix="/api/v1")
app.include_router(question_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(agents_router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CareerPilot AI"}


@app.get("/")
async def root():
    return {
        "name": "CareerPilot AI",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
