from fastapi import FastAPI
import uvicorn
from cyber import  models
from cyber.database import engine
from cyber.routers import blog, user, authentication, elasticsearch
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


models.Base.metadata.create_all(engine)

# app.include_router(authentication.router)
# app.include_router(blog.router)
# app.include_router(user.router)
app.include_router(elasticsearch.router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=9000, reload=True)