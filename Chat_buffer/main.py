from fastapi import FastAPI

from ChatRoute.chat import router as chat_router

app = FastAPI()

app.include_router(chat_router)

@app.get("/")
def root():
    return {"message": "Chatbot API is running! Use the /chat endpoint."}
