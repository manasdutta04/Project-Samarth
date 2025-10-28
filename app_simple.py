import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import requests
from typing import Optional

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

app = FastAPI(title="Project Samarth - Gemini Version")

class Query(BaseModel):
    question: str

class Response(BaseModel):
    answer: str
    sources: Optional[list] = []

@app.get("/")
async def root():
    return {
        "message": "Project Samarth - Q&A System for Indian Agricultural Data",
        "status": "running",
        "ai_model": "Google Gemini 2.5 Flash"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(query: Query):
    """
    Answer questions about Indian agriculture using Gemini AI
    """
    try:
        # Create a prompt with context
        prompt = f"""You are an AI assistant specialized in Indian agricultural data from data.gov.in.
        
User Question: {query.question}

Please provide a detailed, accurate answer based on what you know about Indian agriculture, climate patterns, and farming practices. If you're making claims about specific data, mention that the user should verify with data.gov.in for the latest statistics.

Focus on:
- Agricultural production and trends
- Climate patterns affecting farming
- State-wise variations
- Crop-specific information
- Government policies and initiatives

Answer:"""

        # Get response from Gemini
        response = model.generate_content(prompt)
        
        return Response(
            answer=response.text,
            sources=["Google Gemini 2.5 Flash", "General knowledge about Indian agriculture"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datasets")
async def list_datasets():
    """
    Fetch sample datasets from data.gov.in
    """
    try:
        # Example: Fetch some agriculture-related datasets
        url = "https://data.gov.in/api/datastore/resource.json"
        params = {
            "resource_id": "9ef84268-d588-465a-a308-a864a43d0070",  # Example resource
            "api-key": os.getenv("DATA_GOV_API_KEY", ""),
            "limit": 10
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "message": "Sample datasets endpoint",
                "note": "Configure DATA_GOV_API_KEY for live data access",
                "sample_topics": [
                    "Agricultural Production",
                    "Climate Data",
                    "Crop Prices",
                    "Rainfall Patterns",
                    "Soil Health"
                ]
            }
    except Exception as e:
        return {
            "message": "Datasets endpoint",
            "error": str(e),
            "sample_topics": [
                "Agricultural Production",
                "Climate Data",
                "Crop Prices"
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
