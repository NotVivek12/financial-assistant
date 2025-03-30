import os
import pandas as pd
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import google.generativeai as genai
from dotenv import load_dotenv
import uvicorn
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
app = FastAPI(title="Financial Assistant API")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
products_df = pd.read_csv("data/investment_products.csv")
model = genai.GenerativeModel('gemini-1.5-pro')

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    products_str = products_df.to_string()
    
    prompt = f"""
    You are a financial advisor in India helping users make better investment decisions.
    Answer the following question about investing in India:
    
    User Question: {question}
    
    Available Investment Products:
    {products_str}
    
    Provide a clear, concise response with practical advice. If recommending products, 
    explain why they might be suitable. Include basic information about risk, expected returns, 
    and minimum investment needed. Avoid giving specific tax advice without disclaimers.
    """
    
    try:
        response = model.generate_content(prompt)
        return {"response": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_products(risk_level: str = None, min_investment: int = None):
    filtered_df = products_df
    
    if risk_level:
        filtered_df = filtered_df[filtered_df['risk_level'] == risk_level]
    
    if min_investment:
        filtered_df = filtered_df[filtered_df['min_investment'] <= min_investment]
    
    return filtered_df.to_dict(orient="records")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)