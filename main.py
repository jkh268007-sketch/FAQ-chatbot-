import json
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# =========================
# SETTINGS
# =========================
FAQ_FILE = "faq.json"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "tinyllama"

# =========================
# APP
# =========================
app = FastAPI(title="FAQ Chatbot - No DB")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class ChatRequest(BaseModel):
    user_id: str = "web"
    question: str

class ChatResponse(BaseModel):
    answer: str
    source_faqs: list

# =========================
# LOAD FAQ
# =========================
with open(FAQ_FILE, "r", encoding="utf-8") as f:
    FAQ_DATA = json.load(f)

# =========================
# SEARCH FAQ
# =========================
def find_faq_answer(question: str):
    q = question.lower()

    for faq in FAQ_DATA:
        if faq["question"].lower() in q:
            return faq["answer"], faq["id"]

    return None, None

# =========================
# OLLAMA
# =========================
def ask_ollama(prompt: str):

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
    except Exception:
        return "⚠️ Ollama is not running. Start it with: ollama run tinyllama"

    if resp.status_code != 200:
        return "⚠️ Ollama returned an error."

    data = resp.json()
    return data.get("response", "No response from model")


# =========================
# ROUTES
# =========================
@app.get("/")
def home():
    return {"status": "OK", "message": "FAQ + Ollama Chatbot Running (No DB)"}


@app.post("/chat", response_model=ChatResponse)
def chat(data: ChatRequest):

    question = data.question.strip()

    if not question:
        raise HTTPException(400, "Question is empty")

    # 1. Try FAQ
    faq_answer, faq_id = find_faq_answer(question)

    if faq_answer:
        return ChatResponse(
            answer=faq_answer,
            source_faqs=[faq_id]
        )

    # 2. Use Ollama
    ai_answer = ask_ollama(question)

    return ChatResponse(
        answer=ai_answer,
        source_faqs=[]
    )
