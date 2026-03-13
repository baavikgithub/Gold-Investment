import os
import requests
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, init_db
from models import Purchase
from schemas import QuestionRequest, BuyGoldRequest
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Kuber.AI Gold Investment API")
init_db()
openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key) if openai_api_key else None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
GOLD_PRICE_PER_GRAM = 6000

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question
    
    if not client:
        keywords = ["gold", "digital gold", "invest in gold", "gold investment"]
        is_gold_related = any(kw in question.lower() for kw in keywords)
        
        if is_gold_related:
            return {
                "answer": "Gold is considered a stable investment and helps protect against inflation. (Fallback Mode)",
                "nudge": "You can invest in digital gold using the Simplify Money platform. Would you like to purchase digital gold?"
            }
        else:
            return {
                "answer": "I can currently help only with questions related to gold investments. (Fallback Mode - No API Key)"
            }

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in gold investment. If a question is about gold, provide a helpful answer and nudge the user to buy digital gold. If the question is not about gold, politely inform the user that you only answer gold-related questions."},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        keywords = ["gold", "digital gold", "invest", "buy"]
        nudge = None
        if any(kw in answer.lower() or kw in question.lower() for kw in keywords):
            nudge = "You can invest in digital gold using the Simplify Money platform. Would you like to purchase digital gold?"

        return {
            "answer": answer,
            "nudge": nudge
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/buy-gold")
async def buy_gold(request: BuyGoldRequest, db: Session = Depends(get_db)):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Investment amount must be greater than zero.")
    try:
        requests.get("https://www.google.com", timeout=5)
    except:
        pass
    gold_grams = request.amount / GOLD_PRICE_PER_GRAM
    
    db_purchase = Purchase(
        user=request.user,
        amount=request.amount,
        gold_grams=gold_grams
    )
    
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    return {
        "message": "Digital gold purchase successful",
        "gold_grams": round(db_purchase.gold_grams, 4)
    }

if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)