from fastapi import FastAPI
from pydantic import BaseModel
import requests
import random

app = FastAPI()

# 🔑 PUT YOUR OPENROUTER KEY HERE
OPENROUTER_API_KEY = "sk-xxxxxxxxxxxxxxxx"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json"
}

# ---------------------------
# DATA MODEL
# ---------------------------

class Conversation(BaseModel):
    text: str

# ---------------------------
# MEMORY TEST SYSTEM
# ---------------------------

memory_prompts = [
    ("I had toast this morning.", "What did I say I had this morning?"),
    ("I spoke to my friend John earlier.", "Who did I speak to earlier?"),
    ("I went to the park yesterday.", "Where did I go yesterday?")
]

active_memory = None

# ---------------------------
# HISTORY STORAGE
# ---------------------------

history = []

# ---------------------------
# ANALYSIS FUNCTION
# ---------------------------

def analyze_text(text):
    words = text.split()

    repetition_score = len(words) - len(set(words))

    confusion_keywords = ["uh", "um", "forgot", "don't know", "can't remember"]
    confusion_score = sum(text.lower().count(k) for k in confusion_keywords)

    memory_fail_keywords = ["don't remember", "forgot", "not sure"]
    memory_fail_score = sum(text.lower().count(k) for k in memory_fail_keywords)

    ml_score = random.uniform(0, 1)

    total_score = (
        repetition_score * 0.2 +
        confusion_score * 0.3 +
        memory_fail_score * 1.0 +
        ml_score * 5
    )

    return total_score, {
        "repetition": repetition_score,
        "confusion": confusion_score,
        "memory_fail": memory_fail_score,
        "ml_score": ml_score
    }

def classify(score):
    if score < 2:
        return "Low risk – continue normal monitoring"
    elif score < 4:
        return "Moderate risk – monitor closely"
    else:
        return "High risk – recommend seeing a doctor"

# ---------------------------
# OPENROUTER CHAT
# ---------------------------

def openrouter_chat(system_prompt, user_text):
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=HEADERS,
        json=payload
    )

    data = response.json()

    if "choices" not in data:
        print(data)
        return "Error: API issue"

    return data["choices"][0]["message"]["content"]

# ---------------------------
# CHAT ENDPOINT
# ---------------------------

@app.post("/chat")
def chat(conv: Conversation):
    global active_memory

    system_prompt = (
        "You are a friendly, warm AI companion talking to an elderly person. "
        "Keep sentences simple and conversational."
    )

    if random.random() < 0.5:
        active_memory = random.choice(memory_prompts)
        system_prompt += f" Casually mention this: '{active_memory[0]}'"

    if active_memory and random.random() < 0.5:
        system_prompt += f" Later, ask: '{active_memory[1]}'"

    reply = openrouter_chat(system_prompt, conv.text)

    return {"reply": reply}

# ---------------------------
# ANALYZE ENDPOINT
# ---------------------------

@app.post("/analyze")
def analyze(conv: Conversation):
    score, details = analyze_text(conv.text)
    result = classify(score)

    history.append(score)

    return {
        "score": score,
        "details": details,
        "result": result,
        "history": history
    }
