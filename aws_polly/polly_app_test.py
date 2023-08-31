from fastapi import FastAPI
from fastapi.responses import FileResponse
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
import os
from tempfile import gettempdir
import uvicorn


app = FastAPI()


def polly_start(session):
    polly = session.client("polly")
    response = polly.synthesize_speech(Text=a, OutputFormat="mp3", VoiceId="Joanna")
    return response

def aws_auth():
    aws_access_key_id = "aaaa"
    aws_secret_access_key = "aaaa"

    # AWS 자격증명 확인 및 세션 생성
    try:
        session = Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name="ap-northeast-2"
        )
        return session
    except (BotoCoreError, ClientError) as error:
        return {"error": str(error)}


@app.get("/")
def main():
    return "root page"

@app.get("/synthesize/{text}")
async def synthesize_speech(text: str):
    a = text  

    aws_access_key_id = "aaaa"
    aws_secret_access_key = "aaaa"

    # AWS 자격증명 확인 및 세션 생성
    session = aws_auth()
    response = polly_start(session=session)

    # 음성 데이터 처리 및 파일 생성
    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(), "speech.mp3")
            try:
                with open(output, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                return {"error": str(error)}

        return FileResponse(output, media_type="audio/mpeg")
    else:
        return {"message": "Failed to retrieve audio data."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
