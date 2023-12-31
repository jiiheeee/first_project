from fastapi import FastAPI, Form, status, Request
import uvicorn
from dotenv import load_dotenv
import os
import pymysql
from fastapi.responses import RedirectResponse
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
# from starlette.responses import TemplateResponse
import boto3
from fastapi.responses import JSONResponse

# 템플릿 폴더를 현재 디렉토리로 설정합니다.
templates = Jinja2Templates(directory='templates')

app = FastAPI(docs_url="/documentation", redoc_url=None)

load_dotenv()


# 정적 파일 디렉토리 경로
app.mount("/static", StaticFiles(directory="static"), name="static")

aws_access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
region_name = 'ap-northeast-2'

# ! 이거는 로컬에서 테스트 할때 쓰는거
connection = pymysql.connect(
    host='localhost',
    user='root',
    password='1234',
    database='mydatabase'
)
# ! 이거는 로컬에서 테스트 할때 쓰는거

# # ? 이거는 도커 컨테이너에서 쓰는거
# connection = pymysql.connect(
#     host='mysql',
#     user='root',
#     password='1234',
#     database='mydatabase'
# )
# #? 이거는 도커에서 테스트 할때 쓰는거

# 클라이언트
def create_service_name_client(service_name):
    return boto3.client(
        service_name,
        region_name='ap-northeast-2',
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )

# 메인 페이지
@app.get('/')
def main_page(request:Request):
  return templates.TemplateResponse("main_page.html", {'request':request})

# 회원가입
@app.post('/sign_up')
def sign_up(request:Request):
  return templates.TemplateResponse("sign_up.html", {'request':request})

# 로그인

@app.post('/login')
def login(request:Request):
  return templates.TemplateResponse("login.html", {'request':request})

@app.get('/login/fail')
def login_fail(request:Request):
    error_message = 'Please check your name and password'
    return templates.TemplateResponse("login_fail.html", {'request':request, 'error_message':error_message})

# 회원가입 후 게임 시작
@app.post('/save')
def save(name: str = Form(...), password: str = Form(...)):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
        onion = cursor.fetchall()
        
        if onion:
            message = "이미 존재하는 이름입니다."
            return JSONResponse(content={"message": message}, status_code=400)
        try:
            for name_data, password_data in zip(name, password):
                if name_data == "'" or password_data == "'":
                    error_message = "이름과 비밀전호 중 작은따옴표('') 및 큰따옴표(\"\")는 사용할 수 없습니다."
                    return JSONResponse(content={"message": error_message}, status_code=400)
            cursor.execute(f"INSERT INTO onion (name, level, exp, max_exp, password, image, PN, NN) VALUES ('{name}', 1, 0, 150, '{password}', '/static/level_1', 0, 0)")
            connection.commit()    
            return RedirectResponse(url ="/", status_code=status.HTTP_303_SEE_OTHER)

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return templates.TemplateResponse(
                "error_page.html",
                {"request":{"error_message": "An error occurred"}}  # "request" 키를 추가
    )

# 게임 시작 (키우기)
@app.post('/game_start', response_class=HTMLResponse)
def game_start(name: str = Form(...), password: str = Form(...)):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM onion WHERE name = %s and password = %s", (name, password))
        res = cursor.fetchone()

        #기존 데이터 불러오기#
        if res:
            level = res[1]
            exp = res[2]
            max_exp = res[3]
            image = res[4]
            print(res)
            return templates.TemplateResponse("game_start.html", {"request": {"name": name, "level": level, "exp": exp, "max_exp": max_exp, "image": image}})
        
        #DB에 데이터가 없을 경우#
        elif res == None:
            return RedirectResponse(url ="/login/fail", status_code=status.HTTP_303_SEE_OTHER)

# 대화하기 (번역 + 감정 분석)
@app.post('/analyze_sentiment')
async def analyze_sentiment(text: str = Form(...), name:str = Form(...)):
    try:
        translate_model = create_service_name_client('translate')
        comprehend_model = create_service_name_client('comprehend')

        source_language_code = "ko"  
        target_language_code = "en" 

        result = translate_model.translate_text(
            Text=text,
            SourceLanguageCode=source_language_code,
            TargetLanguageCode=target_language_code
        )

        translated_text = result['TranslatedText']
        if translated_text != text:
            sentiment_result = comprehend_model.detect_sentiment(Text=translated_text, LanguageCode='en')
            sentiment = sentiment_result['Sentiment']

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM onion WHERE name = %s", (name,))
                res = cursor.fetchone()

                level = int(res[1])
                exp = int(res[2])
                max_exp = int(res[3])
                image = res[4]
                positive_number = int(res[6])
                negative_number = int(res[7])

                score = sentiment_result['Sentiment'].capitalize()

                if sentiment == "POSITIVE":
                    new_exp = exp + int(100*sentiment_result['SentimentScore'][f'{score}'])
                    current_image = f'/static/level_{level}'
                    update_PN = positive_number + 1

                    # level up
                    if level <= 4 and new_exp >= max_exp:
                        level_up_level = level + 1
                        level_up_image = f'/static/level_{level_up_level}'
                        level_up_exp = int(new_exp - max_exp)
                        level_up_max_exp = 150 * level_up_level
                        if level_up_level <= 4:
                            cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s, image = %s, PN = %s WHERE name = %s",
                                (level_up_level, level_up_exp, level_up_max_exp, level_up_image, update_PN, name))
                            connection.commit()
                            return templates.TemplateResponse("sentiment.html",
                                {"request":{"name": name, "level": level_up_level, "exp": level_up_exp, "max_exp": level_up_max_exp, "image": level_up_image, "sentiment": sentiment}})
                        elif level_up_level >= 5:
                            return templates.TemplateResponse("ending.html", {"request":{"PN": update_PN}})

                    cursor.execute("UPDATE onion SET exp = %s, image = %s, PN = %s WHERE name = %s",(new_exp, current_image, update_PN, name))
                    connection.commit()
                    return templates.TemplateResponse("sentiment.html",
                        {"request": {"name": name, "level": level, "exp": new_exp, "max_exp": max_exp, "image": current_image, "sentiment": sentiment}})

                elif sentiment == "NEGATIVE":
                    new_exp = exp - int(100*sentiment_result['SentimentScore'][f'{score}'])
                    current_image = f'/static/level_{level}'
                    update_NN = negative_number + 1

                    # game over: 레벨 1 일때 경험치가 마이너스 되면 game over 후 DB에서 삭제
                    if level == 1 and new_exp < 0:
                        cursor.execute(f"delete from onion where name = '{name}'")
                        connection.commit()

                        return templates.TemplateResponse('game_over.html', {"request":{}})

                    # 강등: 현재 레벨 - 1하고 마이너스된 만큼 경험치 차감
                    if new_exp < 0:
                        relegation_max_exp = int(max_exp-150)
                        relegation_exp = relegation_max_exp - abs((exp-int(100*sentiment_result['SentimentScore'][f'{score}'])))
                        relegation_level = int(level - 1)
                        relegation_image = f'/static/level_{relegation_level}'
                        cursor.execute("UPDATE onion SET level = %s, exp = %s, max_exp = %s, image = %s, NN = %s WHERE name = %s",
                                (relegation_level, relegation_exp, relegation_max_exp, relegation_image, update_NN, name))
                        connection.commit()
                        return templates.TemplateResponse("sentiment.html",
                            {"request": {"name": name, "level": relegation_level, "exp": relegation_exp, "max_exp": relegation_max_exp, "image": relegation_image, "sentiment": sentiment}})

                    # 경험치만 차감: 레벨은 동결
                    cursor.execute("UPDATE onion SET exp = %s, image = %s, NN = %s WHERE name = %s",(new_exp, current_image, update_NN, name))
                    connection.commit()
                    return templates.TemplateResponse("sentiment.html",
                        {"request": {"name": name, "level": level, "exp": new_exp, "max_exp": max_exp, "image": current_image, "sentiment": sentiment}})

                else:
                    return templates.TemplateResponse("sentiment.html", {"request": {"name": name, "level": level, "exp": exp, "max_exp": max_exp, "image": image, "sentiment": sentiment}})

        elif translated_text == text:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM onion WHERE name = %s", (name))
                    res = cursor.fetchone()

                    level = int(res[1])
                    exp = int(res[2])
                    image = res[4]
                    max_exp = int(res[3])

                return templates.TemplateResponse("sentiment.html", {"request": {"name": name, "level": level, "image": image, "exp": exp, "max_exp": max_exp}})

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return templates.TemplateResponse(
            "error_page.html",
            {"request":{"error_message": "An error occurred"}}  # "request" 키를 추가
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)