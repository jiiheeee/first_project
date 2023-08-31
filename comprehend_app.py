from fastapi import FastAPI, HTTPException, Request, Form
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

app = FastAPI()

load_dotenv()

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
    try:
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
                
                return res

    except Exception as e:
        return {"error": str(e)}

templates = Jinja2Templates(directory="templates")

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
  
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)