from fastapi import FastAPI, HTTPException
import boto3
import uvicorn

app = FastAPI()

aws_access_key_id = 'aaaa'
aws_secret_access_key = 'aaaa'
region_name = 'ap-northeast-2'  # AWS 리전 선택

@app. get('/')
async def main():
    return "main page`"

# 감정 분석 + 언어 번역
@app.get('/analyze_sentiment/{text}')
async def analyze_sentiment(text: str):

    client_text = text

    translate = boto3.client(
    'translate',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
    )

    text_to_translate = client_text
    source_language_code = "ko"  
    target_language_code = "en" 

    result = translate.translate_text(
        Text=text_to_translate,
        SourceLanguageCode=source_language_code,
        TargetLanguageCode=target_language_code
    )

    translated_text = result['TranslatedText']
    print("Translated Text:", translated_text)

    try:
        comprehend = boto3.client(
            service_name='comprehend', 
            region_name='ap-northeast-2', 
            aws_access_key_id = "aaaa",
            aws_secret_access_key = "aaaa"
        )
        sentiment_result = comprehend.detect_sentiment(Text=translated_text, LanguageCode='en')

        print(sentiment_result)

        sentiment = sentiment_result['Sentiment']


        if sentiment == "POSITIVE":
            return "긍정적인 말을 하시네요."
        elif sentiment == "NAGATIVE":
            return "부정적인 말을 하시네요."
        elif sentiment == "MIXED":
            return "중성적인 말을 하시네요."
        else:
            return "그렇군요"

    except Exception as e:
        raise HTTPException(status_code=500, detail = "Error processing sentiment analysis")

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
