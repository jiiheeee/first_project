from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import boto3
import uvicorn

app = FastAPI()


@app. get("/")
async def main():
    return "hi"

@app.get("/analyze_sentiment/{text}")
async def analyze_sentiment(text: str):

    a = text

    try:
        comprehend = boto3.client(
            service_name='comprehend', 
            region_name='ap-northeast-2', 
            aws_access_key_id = "aaaa",
            aws_secret_access_key = "aaaa"
        )
        sentiment_result = comprehend.detect_sentiment(Text=a, LanguageCode='ko')
        return sentiment_result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail = "Error processing sentiment analysis")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)