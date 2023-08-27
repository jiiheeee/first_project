import boto3

# AWS 자격 증명 및 클라이언트 설정
aws_access_key_id = 'AKIAUVG62NWBONCNAMHU'
aws_secret_access_key = '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'
region_name = 'ap-northeast-2'  # AWS 리전 선택

translate = boto3.client(
    'translate',
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name
    )

text_to_translate = "Hello, how are you?"
source_language_code = "en"  # 원본 언어 코드 (예: 영어 - en)
target_language_code = "ko"  # 대상 언어 코드 (예: 프랑스어 - fr)

response = translate.translate_text(
    Text=text_to_translate,
    SourceLanguageCode=source_language_code,
    TargetLanguageCode=target_language_code
)

translated_text = response['TranslatedText']
print("Translated Text:", translated_text)
