#CLOVA api

import requests
import json
import pandas as pd
from .utils import env


class STT:
    def get_script_from_video(self, video_path:str, language:str, save_dir:str) -> pd.DataFrame:
        """
        Generate a script from video
        
        Parameters:
            video_path ('str'): Path to video file
            langauge ('str'): Language in video.
            save_dir ('str'): Directory where the script CSV file is saved (will be created if it does not exist).
        
        Returns
            'pd.DataFrame': Information of each lines. Sequence of (start, end, text, langauge)

        """
        raise NotImplementedError()
    

class ClovaSTT(STT):
    def __init__(self):
        #You must get below two parameters by your own CLOVA account:
        #Console -> Clova Speech -> Service Builder
        #You might have to also use ObjectStorage
        #put them into autodub/env.yaml

        # Clova Speech invoke URL
        self._invoke_url = env['CLOVA']['INVOKE_URL']
        # Clova Speech secret key
        self._secret = env['CLOVA']['SECRET']
        self.language_ids = {
            "KO": 'ko-KR',
            "ko": 'ko-KR',
            "korean": "ko-KR",
            "ko-KR": "ko_KR",
            "EN": 'en-US',
            "en": 'en-US',
            "english": 'en-US',
            "en-US": "en-US",
            "JP": "ja",
            "JA": "ja",
            "jp": "ja",
            "ja": "ja",
            "japanese": "ja",
            "CN": "zh-cn",
            "ZH": "zh-cn",
            "cn": "zh-cn",
            "zh": "zh-cn",
            "chinese": "zh-cn",
            "zh-cn": "zh-cn"
        }
    def _call_clova_api(self, video_path, language):
        request_body = {
            'language': 'ko-KR',
            'completion': 'sync',
            'callback': None,
            'wordAlignment': True,
            'fullText': False
        }
        headers = {
            'Accept': 'application/json;UTF-8',
            'X-CLOVASPEECH-API-KEY': self._secret
        }
        files = {
            'media': open(video_path, 'rb'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        response = requests.post(headers=headers, url=self._invoke_url + '/recognizer/upload', files=files)
        return response
    
    def get_script_from_video(self, video_path, language, save_dir=None):
        if not language in self.language_ids.keys():
            raise ValueError(f"Unexpected language: {language}")
        
        clova_response = self._call_clova_api(video_path, self.language_ids[language])
        result_dict = json.loads(clova_response.text)
        # Organize in DataFrame format
        script = []
        for segment in result_dict["segments"]:
            script.append({
                'start': segment['start'],
                'end': segment['end'],
                f'{language}': segment['text'],
            })
        script = pd.DataFrame(script)
        if save_dir is not None:
            script.to_csv(save_dir + "/script.csv", index=False)
        return script
    
    
