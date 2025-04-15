from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Configure Google's Generative AI
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Load investment products data
with open('data/investment_products.json', 'r') as f:
    investment_products = json.load(f)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.post("/ask")
async def ask_question(question: str = Form(...)):
    try:
        # Create a prompt for the AI
        prompt = f"""You are a financial assistant specializing in Indian markets. 
        Please provide a helpful and accurate response to the following question about investing in India:
        {question}
        
        Keep your response concise and focused on Indian markets. If the question is not related to Indian markets,
        politely inform the user that you specialize in Indian markets and suggest rephrasing the question."""

        # Generate response
        response = model.generate_content(prompt)
        
        return JSONResponse(content={"response": response.text})
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while processing your question."}
        )

@app.get("/products")
async def get_products(risk_level: str = None, min_investment: int = None):
    try:
        filtered_products = investment_products.copy()
        
        # Filter by risk level if provided
        if risk_level:
            filtered_products = [p for p in filtered_products if p['risk_level'] == risk_level]
        
        # Filter by minimum investment if provided
        if min_investment:
            filtered_products = [p for p in filtered_products if p['min_investment'] <= min_investment]
        
        return JSONResponse(content=filtered_products)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while fetching products."}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)