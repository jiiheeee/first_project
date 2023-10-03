# 양파 육성 웹 게임

<img alt="game_start image" src="https://github.com/jiiheeee/first_project/assets/128598772/cc8cdc7a-4e3f-44fd-84f5-b02ec0dba596" width="50%">

<img src="https://github.com/jiiheeee/first_project/assets/128598772/e0ca220d-4ad5-47b6-a970-b58fdd3b68d2"/>
![python](https://github.com/jiiheeee/first_project/assets/128598772/e0ca220d-4ad5-47b6-a970-b58fdd3b68d2)
대화창에 문장을 입력하면 AWS Translate API를 사용하여 해당 문장을 영어로 번역하고, AWS Comprehend API를 사용하여 문장의 감정(긍정 또는 부정)을 분석하는 웹 게임입니다. 이 게임에서는 사용자가 양파라는 캐릭터를 육성하며, 특정 경험치에 도달하면 레벨이 증가합니다.

## 개요

프로젝트는 다음과 같은 주요 구성 요소로 이루어져 있습니다:

- 한글 문장을 입력받아 AWS Translate API를 사용하여 영어로 번역합니다.
- 번역된 영어 문장을 AWS Comprehend API를 사용하여 감정 분석을 수행합니다.
- 감정 분석 결과에 따라 경험치를 조절하고 양파 캐릭터를 성장시킵니다.
- 특정 경험치에 도달하면 레벨이 증가하며, 양파 캐릭터가 더 성장합니다.

## 환경 설정

프로젝트는 다음 환경에서 개발 및 배포되었습니다:

- 로컬 환경: M1 맥북
- 배포 환경: AWS EC2 AMI (t2.micro 인스턴스)의 도커 컨테이너
- 사용 언어: Python 3.10

## 기술 스택

프로젝트에서 사용된 주요 라이브러리 및 프레임워크는 다음과 같습니다:

- Python 3.10
- FastAPI 0.103.0
- Uvicorn 0.23.2

## 설치 및 실행

프로젝트를 로컬 환경에서 실행하려면 다음 단계를 따르세요:

1. 프로젝트 레포지토리를 클론합니다.
2. 필요한 패키지를 설치합니다: `pip install -r requirements.txt`
3. Uvicorn을 사용하여 FastAPI 애플리케이션을 실행합니다: `uvicorn main:app --host 0.0.0.0 --port 8000`

웹 게임을 실행한 후, 한글 문장을 입력하면 양파 캐릭터를 성장시키는 데 도움이 됩니다.

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 기여

이 프로젝트에 기여하고 싶다면, 이슈를 제기하거나 풀 리퀘스트를 보내주세요. 우리는 개선을 환영합니다!

