from fastapi import FastAPI, Form, status
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

# 정적 파일 디렉토리 경로
app.mount("/static", StaticFiles(directory="static"), name="static")

class SentimentAnalysisInput(BaseModel):
    text: str

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = 'ap-northeast-2'

app.mount("/static", StaticFiles(directory="static"), name="static")

connection = pymysql.connect(
    host='172.17.0.1',
    user='my_user',
    password='1234',
    database='mydatabase'
)


# #? 이거는 도커 컨테이너에서 쓰는거
# connection = pymysql.connect(
#     host='mysql',
#     user='root',
#     password='1234',
#     database='mydatabase'
# )
# #? 이거는 로컬에서 테스트 할때 쓰는거

# @app.get('/get_image')
# def get_image(image_name: str):
#     image_path = os.path.join('static', f"{image_name}.jpeg")
#     print(1)
#     return FileResponse(image_path, media_type='image/jpeg')

# """ 메인 페이지 """
@app.get('/')
def main_page():
  return FileResponse('main_page.html')

#""" 회원가입 """
@app.post('/sign_up')
def sign_up():
    return FileResponse('sign_up.html')

# """ 로그인 """
@app.post('/login')
def login():
  return FileResponse('login.html')

#  """ 회원가입 후 게임 시작 """
@app.post('/save')
def save(name: str = Form(...), password: str = Form(...)):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
        existing_record = cursor.fetchall()
        
        if existing_record:
            return '이미 존재하는 이름입니다.'
        
        try:
            cursor.execute(f"INSERT INTO onion (name, level, exp, max_exp, password) VALUES ('{name}', 1, 0, 100, '{password}')")
            connection.commit()    
            return RedirectResponse(url ="/", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
            print(str(e))
            return '에러남 ㅜ'
        



    # 현재 스크립트의 경로를 가져옵니다.
current_dir = Path(__file__).resolve().parent
    # 템플릿 폴더를 현재 디렉토리로 설정합니다.
templates = Jinja2Templates(directory=current_dir)

# """ 게임 시작 (키우기) """
@app.post('/game_start', response_class=HTMLResponse)
def game_start(name: str = Form(...), password: str = Form(...)):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s and password = %s", (name, password))
        res = cursor.fetchone()
        if res:
            level = res[1]
            exp = res[2]
            max_exp = res[3]
            return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": level, "exp": exp, "max_exp": max_exp}})
        else:
            return '아이디 혹은 비밀번호를 확인해주세요.'

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

                if new_exp >= current_max_exp:
                    new_level = current_level + 1
                    new_exp = abs(int(current_max_exp - new_exp))
                    new_max_exp = 300 * new_level 
                    cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s WHERE name = %s",
                            (new_level, new_exp, new_max_exp, name))
                    connection.commit()
                    return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": new_level, "exp": new_exp, "max_exp": new_max_exp}})
                
                cursor.execute("UPDATE onion SET exp = %s WHERE name = %s",
                        (new_exp, name))
                connection.commit()
                return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": current_level, "exp": new_exp, "max_exp": current_max_exp}})

            elif sentiment == "NEGATIVE":
                new_exp = current_exp - int(10*sentiment_result['SentimentScore'][f'{score}'])
                
            
                if  current_level == 1:
                    if new_exp <= 0:
                        cursor.execute(f"delete from onion where name = '{name}'")
                        
                        return FileResponse('game_over.html')

                    else:
                       cursor.execute("UPDATE onion SET exp = %s WHERE name = %s",
                        (new_exp, name))
                       connection.commit()
                       return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": current_level, "exp": new_exp, "max_exp": current_max_exp}})
                
                elif current_level > 1:
                    if new_exp < 0:
                        new_max_exp = int(current_max_exp/(3*current_level))
                        new_exp = new_max_exp - abs((current_exp-int(10*sentiment_result['SentimentScore'][f'{score}'])))
                        new_level = int(current_level - 1)

                        cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s WHERE name = %s",
                        (new_level, new_exp, new_max_exp, name))
                        connection.commit()
                        return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": new_level, "exp": new_exp, "max_exp": new_max_exp}})
                
                    elif new_exp >= 0:
                        cursor.execute("UPDATE onion SET exp = %s WHERE name = %s",
                        (new_exp, name))
                        connection.commit()
                        return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": current_level, "exp": new_exp, "max_exp": current_max_exp}})
            

               

            cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
            model = cursor.fetchone()
            print(model)

        return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": new_level, "exp": new_exp, "max_exp": new_max_exp, "sentiment": sentiment}})
    except Exception as e:
        print(e)
        return '무슨 말씀인지 모르겠어요 ㅜ'

        
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)



"""
    레벨 업 하고 나쁜말하면 다시 강등
"""