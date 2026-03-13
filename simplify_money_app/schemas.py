from pydantic import BaseModel

class QuestionRequest(BaseModel):
    question: str

class BuyGoldRequest(BaseModel):
    user: str
    amount: int