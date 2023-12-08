import os
import requests
import json
import pandas as pd
from .utils import env


class STT:
    def get_script_from_video(self, video_path:str, language:str) -> pd.DataFrame:
        """
        Generate a script from video
        
        Parameters:
            video_path ('str'): Path to video file
            langauge ('str') : Language in video. One of ['KO', 'EN', 'JA', 'CN'].
        
        Returns
            'pd.DataFrame': Information of each lines. Sequence of (start, end, source(text), translation1, translation2, ...)

        """
        raise NotImplementedError()
    

class ClovaSTT(STT):
    def __init__(self):
        '''
        You must get below two parameters by your own CLOVA account
        Follow 'https://guide.ncloud-docs.com/docs/clovaspeech-spec'
        And put them into autodub/env.yaml
        
        CLOVA API Reference:
            https://api.ncloud-docs.com/docs/ai-application-service-clovaspeech-longsentence
        '''
        # Clova Speech invoke URL
        self._invoke_url = env['CLOVA']['INVOKE_URL']
        # Clova Speech secret key
        self._secret = env['CLOVA']['SECRET']
        
        self._get_clova_langid = {
            "ko": "ko-KR",
            "en": 'en-US',
            'ja': 'ja',
            'zh': 'zh-cn'
        }

    def _call_clova_api(self, video_path, language):
        if not language in self._get_clova_langid.keys():
            raise ValueError(f"Unexpected language: {language}")
        else:
            clova_langid = self._get_clova_langid[language]
            
        request_body = {
            'language': clova_langid,
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
    
    def get_script_from_video(self, video_path, language):
        
        clova_response = self._call_clova_api(video_path, language)
        result_dict = json.loads(clova_response.text)
        
        # Organize in DataFrame format
        script = []
        for segment in result_dict["segments"]:
            script.append({
                'start': segment['start'],
                'end': segment['end'],
                'source': segment['text'],
            })
            
        script = pd.DataFrame(script)
        return script
    

class WhisperSTT(STT):
    # TODO: Implement WhisperSTT
    def __init__(self):
        raise NotImplementedError()

    def get_script_from_video(self, video_path: str, language: str) -> pd.DataFrame:
        raise NotImplementedError()
    
    
def load_stt(name:'str') -> STT:
    '''
    Instansiate one of autodub.STT classes
    
    Parameters:
        name ('str'): Target STT. One of ['CLOVA', 'WHISPER', ...]
        
    Returns:
        'STT': Target STT instance
    '''
    match name:
        case "CLOVA": return ClovaSTT()
        case "WHISPER": return WhisperSTT()
        case _: raise ValueError()
        