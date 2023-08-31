from fastapi import FastAPI, Form
import uvicorn
from models import Onion
from aws_translate.language_translate import language_translate
from auth import auth
from dotenv import load_dotenv
import os
import pymysql
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from pydantic import BaseModel

app = FastAPI()

load_dotenv()

class SentimentAnalysisInput(BaseModel):
    text: str

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = 'ap-northeast-2'

app.mount("/static", StaticFiles(directory="static"), name="static")
connection = pymysql.connect(
        host='127.0.0.1',
        user='root',
        password='1234',
        database='mydatabase'
)
@app.get('/get_image')
def get_image(image_name: str):
    image_path = os.path.join('static', f"{image_name}.jpeg")
    print(1)
    return FileResponse(image_path, media_type='image/jpeg')


@app.get('/')
def main_page():
  return FileResponse('main_page.html')

@app.post('/new_model')
def new_model():
  return FileResponse('new_model.html')

@app.post('/search')
def new_model():
  return FileResponse('search.html')


@app.post('/save')
def save_result(name: str = Form(...)):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
        existing_record = cursor.fetchone()
        
        if existing_record:
            return '이미 존재하는 이름입니다.'
        else:
            cursor.execute(f"INSERT INTO onion (name, level, exp, max_exp) VALUES ('{name}', 1, 0, 100)")
            connection.commit()
            cursor.execute(f"select * from onion where name = '{name}'")
            res = cursor.fetchone()
            
            return RedirectResponse("/game_start?name="+ name, status_code=303)
        
# 현재 스크립트의 경로를 가져옵니다.
current_dir = Path(__file__).resolve().parent
# 템플릿 폴더를 현재 디렉토리로 설정합니다.
templates = Jinja2Templates(directory=current_dir)

@app.get('/game_start', response_class=HTMLResponse)
def show_game_start(name: str):
    return templates.TemplateResponse("game_start.html", {"request": {"query": name}})

@app.post('/search_result')
def search(name: str = Form(...)):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM onion WHERE name = %s", (name,))
            res = cursor.fetchone()
            if res[0][0]:
                return res
    except:
        return '검색하신 이름이 없습니다.'

"""
    1. 랜덤으로 새싹키우기 -> 골드까지 키워서 팔기
    2. 팔면 포인트 줌
    3. 그 포인트로 다음 새싹 경험치에 써먹을수있는 쿠폰 드림
"""

# # 감정 분석 + 언어 번역
@app.post('/analyze_sentiment')
def analyze_sentiment(text: str = Form(...), name: str = Form(...)):
    text = text

    translated_text = language_translate(text)

    auth(comprehend)
    comprehend = auth(comprehend)
    sentiment_result = comprehend.detect_sentiment(Text=translated_text, LanguageCode='en')

    print(sentiment_result)

    sentiment = sentiment_result['Sentiment']
    
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM onion WHERE name = %s", (name,))
        res = cursor.fetchall()
        print(res)
        # if sentiment == "POSITIVE":
        #     exp = sentiment_result['SentimentalScore']["Positive"]
        #     r.exp += exp
        # elif sentiment == "NAGATIVE":
        #     exp = sentiment_result['SentimentalScore']["Negative"]
        #     x.exp -= exp
        # else :
        #     exp = 0
    
    

       






# # @app.on_event("startup")
# # async def startup_db_client():
# #     app.db_connection = pymysql.connect(
# #         host="localhost",
# #         user="root",
# #         password="1234",
# #         db="first_database",
#         autocommit=True
#     )

# app.cursor = app.db.cursor()

# @app.on_event("shutdown")
# async def shutdown_db():
#     app.db.close()

# @app.get("/query")
# async def query_database():
#     cursor = app.db_connection.cursor()
#     query = "SELECT * FROM your_table_name"
#     cursor.execute(query)
#     results = cursor.fetchall()
#     cursor.close()
#     return results



#         # 경험치가 100이면 레벨업
#         if 경험치 > x.max_exp:
#             x.level += 1
#             x.max_exp += (300*x.level)
        
#         # x양파를 db에 저장
#         return (x.name, x.level, x.exp, x.max_exp)
            




        


        
        
            
        
        

#     except Exception as e:
#         raise HTTPException(status_code=500, detail = "Error processing sentiment analysis")

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)