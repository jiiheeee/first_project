from fastapi import FastAPI, Form
import uvicorn
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

#""" 새로운 캐릭터 만들기 """
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
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
        res = cursor.fetchone()
        level = res[1]
        exp = res[2]
        max_exp = res[3]
        
    return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": level, "exp": exp, "max_exp": max_exp}})


# """ 이름 검색 결과 및 불러오기"""
@app.post('/search_result')
def search(name: str = Form(...)):
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM onion WHERE name = %s", (name,))
            res = cursor.fetchone()
            level = res[1]
            exp = res[2]
            max_exp = res[3]

            if res[0][0]:
                return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": level, "exp": exp, "max_exp": max_exp}})

    except:
        return '검색하신 캐릭터를 찾지 못했습니다. 이름을 확인해주세요.'

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
    try:
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
            current_max_exp = int(res[3])

            score = sentiment_result['Sentiment'].capitalize()
            

            if sentiment == "POSITIVE":
                new_exp = current_exp + int(10*sentiment_result['SentimentScore'][f'{score}'])
                cursor.execute("UPDATE onion SET exp = %s WHERE name = %s",
                        (new_exp, name))
                connection.commit()

            elif sentiment == "NEGATIVE" and sentiment_result['SentimentScore'][f'{score}']:
                new_exp = current_exp - int(10*sentiment_result['SentimentScore'][f'{score}'])
                
            
                if  current_level == 1 and new_exp <= 0:
                    cursor.execute(f"delete from onion where name = '{name}'")
                    return f'GAME OVER ㅜ'
                
                elif current_level > 1 and new_exp < 0:
                    new_max_exp = int(current_max_exp/current_level)
                    new_exp = new_max_exp - int(10*sentiment_result['SentimentScore'][f'{score}'])
                    new_level = int(current_level - 1)
                 

            

            if new_exp >= res[3]:
                new_level = current_level + 1
                new_max_exp = 300 * new_level 
               

            # cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s WHERE name = %s",
            #             (new_level, new_exp, new_max_exp, name))

            # connection.commit()

            cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
            model = cursor.fetchone()
            print(model)

        return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": new_level, "exp": new_exp, "max_exp": new_max_exp}})
    except:
        return '무슨 말씀인지 모르겠어요 ㅜ'

        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



"""
    레벨 업 하고 나쁜말하면 다시 강등
"""