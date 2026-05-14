from fastapi import FastAPI
from database import engine
import models
from Routes import users

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)


@app.get("/")
def home():
    return {"message": "Notes store API"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
