import boto3

<<<<<<< HEAD
def language_translate(client_text):
    # Boto3 클라이언트를 생성할 때 자동으로 AWS 구성에서 자격 증명을 사용합니다.
    translate = boto3.client(
        'translate',
        aws_access_key_id='AKIAUVG62NWBONCNAMHU',
        aws_secret_access_key='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',
        region_name='ap-northeast-2')
=======
# AWS 자격 증명 및 클라이언트 설정
aws_access_key_id = 'aaaa'
aws_secret_access_key = 'aaaa'
region_name = 'ap-northeast-2'  # AWS 리전 선택
>>>>>>> 06f6fd4e77bc3704405b37b896c162999ece4078

    text_to_translate = client_text
    source_language_code = "ko"
    target_language_code = "en"

    response = translate.translate_text(
        Text=text_to_translate,
        SourceLanguageCode=source_language_code,
        TargetLanguageCode=target_language_code
    )

    translated_text = response['TranslatedText']
    print("Translated Text:", translated_text)
    return translated_text
