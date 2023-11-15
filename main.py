import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from src.conf.config import config
from src.repository.users import update_user_last_request
from src.routes import auth, users, posts, comments, analytics

"""
FastAPI application for a social network.

This application provides backend functionality for a social networking service,
including user authentication, post management, comment handling, and analytics.
It uses Redis for rate limiting and implements CORS middleware for cross-origin resource sharing.
"""

app = FastAPI(title="Social Network", version="0.1.0")

# Apply CORS policy for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to update the last request data for a user
app.middleware('http')(update_user_last_request)

# Including various routers for different functionalities
app.include_router(auth.router)
app.include_router(users.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(comments.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    Perform startup actions for the FastAPI application.

    This function initializes the Redis connection for rate limiting
    and other necessary startup configurations.
    """
    r = await redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        password=config.redis_password,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(r)


@app.get("/")
def read_root():
    """
    Root endpoint for the FastAPI application.

    Returns a welcoming message, indicating the API is functional.
    """
    return {"message": "Welcome to the Social Network API"}


if __name__ == "__main__":
    # Running the application with Uvicorn
    uvicorn.run("main:app", host="localhost", reload=True, log_level="info")
