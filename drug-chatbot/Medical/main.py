from fastapi import FastAPI
from pydantic import BaseModel
from multi_source_agent import answer_multi_source

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    topic: str = "Lung cancer"

@app.get("/")
def root():
    return {"message": "Ask questions via POST /ask"}

@app.post("/ask")
def ask(request: QueryRequest):
    return answer_multi_source(request.topic, request.question)