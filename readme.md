# 양파 육성 웹 게임

<p align="center">
  <img alt="game_start image" src="https://github.com/jiiheeee/first_project/assets/128598772/5c3a3c85-f721-4302-87c7-8e66cb2a7956" width="50%">
</p>

양파 캐릭터를 생성하여 칭찬을 통한 양파 육성 웹 게임입니다. 대화창에 문장을 입력하면 AWS Translate API를 사용하여 해당 문장을 영어로 번역하고, AWS Comprehend API를 사용하여 문장의 감정(긍정 또는 부정)을 분석합니다. 이 게임에서는 사용자가 양파라는 캐릭터를 육성하며, 특정 경험치에 도달하면 레벨이 증가합니다.

## 개요

프로젝트는 다음과 같은 주요 구성 요소로 이루어져 있습니다:

- 회원가입을 통해서 양파를 생성합니다.
- 한글 문장을 입력받아 AWS Translate API를 사용하여 영어로 번역하여 감정 분석에 정확도를 높혀줍니다.
- 번역된 영어 문장을 AWS Comprehend API를 사용하여 감정 분석을 수행합니다.
- 감정 분석 결과에 따라 경험치를 조절하고 양파 캐릭터를 성장시킵니다.
- 특정 경험치에 도달하면 레벨이 증가하며, 양파 캐릭터가 더 성장합니다.
- 게임 오버되면 양파는 자동으로 삭제됩니다.

## 게임 방법

이 게임을 즐기려면 다음 단계를 따르세요:
<div style="position: relative;" align="center">
  <img alt="sign_up" src="https://github.com/jiiheeee/first_project/assets/128598772/36a616c3-dc7e-4034-b191-85a6eb227737" width="30%">
  <p style="position: absolute; top: 10px; left: 10px; font-weignt: bold;"></p>
</div>

1. 양파 생성(회원가입): 게임을 시작하려면 먼저 회원가입을 해야 합니다. 홈페이지에서 회원가입 양식을 작성하고 계정을 생성하세요.
  <p align="center">
    <img alt="login" src="https://github.com/jiiheeee/first_project/assets/128598772/fb6f1d88-1044-4f4c-aa4f-16257475185f" width="30%">
  </p>
2. 로그인: 회원가입이 완료되면 생성된 계정으로 로그인하세요. 생성된 양파 캐릭터는 초기 레벨 1에서 시작합니다.

  <p align="center">
    <img alt="game_start" src="https://github.com/jiiheeee/first_project/assets/128598772/484e5b37-1b2a-49c3-8acd-9e23fdb463e8" width="30%">
  </p>
3. 게임 시작: 생성된 양파 캐릭터에게 칭찬을 해주세요. 칭찬을 하면 양파 캐릭터의 경험치가 증가합니다.

4. 레벨 업: 양파 캐릭터의 경험치가 일정 수준에 도달하면 레벨이 증가합니다. 레벨이 오를수록 양파 캐릭터가 성장합니다.

5. 엔딩: 레벨 4에 도달하면 게임이 끝나고, 그동안 양파에게 한 칭찬 횟수에 따라 다른 엔딩 이미지가 표시됩니다. 칭찬을 많이 한 만큼 특별한 엔딩을 볼 수 있습니다.


## 환경 설정

프로젝트는 다음 환경에서 개발 및 배포되었습니다:

- 로컬 환경: M1 맥북
- 배포 환경: AWS EC2 AMI (t2.micro 인스턴스)의 도커 컨테이너
- 사용 언어: Python 3.10

## 기술 스택

프로젝트에서 사용된 주요 라이브러리 및 프레임워크는 다음과 같습니다:

- Programming: <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white">  3.10 
- Framwork: <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white">  0.103.0 
- Amazon AWS EC2, Comprehend, Translate <img src="https://img.shields.io/badge/Amazon AWS-232F3E?style=for-the-badge&logo=Amazon AWS&logoColor=white">
- PyMySQL <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=MySQL&logoColor=white">  1.1.0 
- Uvicorn 0.23.2

## 설치 및 실행

프로젝트를 실행하려면 오른쪽 링크를 눌러주세요.
[SUPERION, BADION](http://ec2-3-36-70-35.ap-northeast-2.compute.amazonaws.com:8000/)


