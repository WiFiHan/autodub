# papago 번역 API 사용 - 함수 활용
import requests
import json
import os
import yaml

# For env file
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.join(script_dir, '..'))
file_path = 'env.yaml'
with open(file_path) as f:
    env = yaml.full_load(f)

# translate 함수 선언
def translate(text, source, target):
    #GET CLIENT_ID, CLIENT_SECRET from "NAVER DEVELOPER CENTER", INSTEAD OF CLOVA and write down to env.yaml
    CLIENT_ID, CLIENT_SECRET = env['PAPAGO']['ID'], env['PAPAGO']['SECRET']
    #DO NOT CHANGE URL
    url = 'https://openapi.naver.com/v1/papago/n2mt'
    headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    data = {'source': source, 'target': target, 'text': text}
    response = requests.post(url, json.dumps(data), headers=headers)

    result = response.json()['message']['result']['translatedText']
    return result
