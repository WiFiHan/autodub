import os
from abc import  abstractmethod
import requests
import json
import pandas as pd
from moviepy.editor import VideoFileClip
import whisper_timestamped as whisper
from .utils import env, extract_audio_from_video
from .script import MultilingualScript

class STT:
    @abstractmethod
    def make_script_from_video(self, video_path:str, language:str, title:str) -> MultilingualScript:
        """
        Generate a script from video
        
        Parameters:
            video_path ('str') : Path to video file
            langauge ('str') : Language in video. One of ['KO', 'EN', 'JA', 'CN'].
            title ('str') : Title of script. Use for making checkpoint dir, etc.

        Returns
            'autodub.script.MultilingualScript': 
                A 'MultilingualScript' containing information of the given video
        """
        pass
    

class ClovaSTT(STT):
    def __init__(self):
        '''
        You must get below two parameters by your own CLOVA account
        Follow 'https://guide.ncloud-docs.com/docs/clovaspeech-spec'
        And put them into './env.yaml'
        
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

    def _call_clova_api(self, video_path:str, language:str):
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
    
    def make_script_from_video(self, 
                               video_path:str, 
                               language:str, 
                               title:str,
                               ) -> MultilingualScript:
        clova_response = self._call_clova_api(video_path, language)
        result_dict = json.loads(clova_response.text)
        
        audio_output_path = f'./results/{title}/audio/source.wav'
        if not os.path.exists(os.path.dirname(audio_output_path)):
            os.makedirs(os.path.dirname(audio_output_path))
        source_video = video_path

        # Organize in DataFrame format.
        data = []
        for segment in result_dict["segments"]:
            data.append({
                'start': segment['start'],
                'end': segment['end'],
                'source': segment['text'],
            })
        data = pd.DataFrame(data)
        
        return MultilingualScript(title=title, 
                                  video_path=video_path,
                                  audio_path=audio_output_path,
                                  source_language=language, 
                                  data=data)
    

class WhisperSTT(STT):
    def __init__(self):
        pass

    def make_script_from_video(self, video_path: str, language: str, title: str) -> MultilingualScript:
        

        audio_output_path = f'./results/{title}/audio/source.wav'
        if not os.path.exists(os.path.dirname(audio_output_path)):
            os.makedirs(os.path.dirname(audio_output_path))
        audio = whisper.load_audio(audio_output_path)
        
        model = whisper.load_model("medium", download_root=os.path.join(os.getcwd(), "whisper"))
        result_dict = whisper.transcribe(model, audio, language)

        data = []
        for segment in result_dict["segments"]:

            data.append({
                'start': int(float(segment['start']) * 1000),
                'end': int(float(segment['end'])*1000),
                'source': segment['text'],
            })  
        data = pd.DataFrame(data)
        
        print(f'video_path is {video_path}. stt.py line 130')

        return MultilingualScript(title=title, 
                                  video_path=video_path,
                                  audio_path=audio_output_path,
                                  source_language=language, 
                                  data=data)
    
    
def load_stt(name:'str') -> STT:
    '''
    Instansiate one of STT classes
    
    Parameters:
        name ('str'): Target STT. One of ['CLOVA', 'WHISPER', ...]
        
    Returns:
        'STT': Target STT instance
    '''
    match name:
        case "CLOVA": return ClovaSTT()
        case "WHISPER": return WhisperSTT()
        case _: raise ValueError()
        
