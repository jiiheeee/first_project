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
import boto3


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

# """ 메인 페이지 """
@app.get('/')
def main_page():
  return FileResponse('main_page.html')

#""" 새로운 모델 만들기 """
@app.post('/new_model')
def new_model():
  return FileResponse('new_model.html')

# """ 이름 검색"""
@app.post('/search')
def new_model():
  return FileResponse('search.html')

#  """새 모델 저장 후 게임 시작"""
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

# """ 게임 시작 (키우기) """
@app.get('/game_start', response_class=HTMLResponse)
def show_game_start(name: str):
    return templates.TemplateResponse("game_start.html", {"request": {"query": name}})

# """ 이름 검색 결과 """
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

#  """ 번역 클라이언트 """
def create_translate_client():
    return boto3.client(
        'translate',
        region_name='ap-northeast-2',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

#  """ 감정 분석 클라이언트 """
def create_comprehend_client():
    return boto3.client(
        'comprehend',
        region_name='ap-northeast-2',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

#  """ 대화하기  (번역 + 감정 분석) """
@app.post('/analyze_sentiment')
async def analyze_sentiment(text: str = Form(...), name:str = Form(...)):

    translate = create_translate_client()
    comprehend = create_comprehend_client()

    client_text = text
    
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

    sentiment_result = comprehend.detect_sentiment(Text=translated_text, LanguageCode='en')

    print(sentiment_result)

    sentiment = sentiment_result['Sentiment']

    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
        res = cursor.fetchone()
        print(res)

        current_level = int(res[1])
        current_exp = int(res[2])

        score = sentiment_result['Sentiment'].capitalize()
        

        if sentiment == "POSITIVE":
            new_exp = current_exp + int(10*sentiment_result['SentimentScore'][f'{score}'])

        elif sentiment == "NEGATIVE" and current_exp <= 0:
            cursor.execute(f"delete from onion where name = '{name}'")
            return f'GAME OVER ㅜ'
        
        elif sentiment == "NEGATIVE":
            new_exp = current_exp - int(10*sentiment_result['SentimentScore'][f'{score}'])

        if new_exp >= res[3]:
            new_level = current_level + 1
            new_max_exp = 300 * new_level
        else:
            new_level = current_level
            new_max_exp = res[3]

        

        cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s WHERE name = %s",
                       (new_level, new_exp, new_max_exp, name))

        connection.commit()

    return {"name": name, "level": new_level, "exp": new_exp, "max_exp": new_max_exp}
    
        # if sentiment == "POSITIVE":
        #     return "긍정적인 말을 하시네요."
        # elif sentiment == "NAGATIVE":
        #     return "부정적인 말을 하시네요."
        # elif sentiment == "MIXED":
        #     return "중성적인 말을 하시네요."
        # else:
        #     return "그렇군요"

       






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