import json
import requests
import pandas as pd
from .utils import env

class Translator:
    def translate_script(script:pd.DataFrame, source_language:str, target_language:str, save_dir=None) -> pd.DataFrame:
        """
        Translate each lines in the script.
        
        Parameters:
            script ('pd.DataFrame') 
            source_language ('str') 
            target_language ('str') 
            save_dir ('str') 
            
        Returns
            'pd.DataFrame': Script with target language added
        """
        raise NotImplementedError()


class PapagoTranslator(Translator):
    def __init__(self):
        self._id = env['PAPAGO']['ID']
        self._secret =  env['PAPAGO']['SECRET']
        self._url = env['PAPAGO']['URL']
        self.language_ids = {
            "KO": 'ko',
            "ko": 'ko',
            "korean": "ko",
            "ko-KR": "ko",
            "EN": 'en',
            "en": 'en',
            "english": 'en',
            "en-US": "en",
            "JP": "ja",
            "JA": "ja",
            "jp": "ja",
            "ja": "ja",
            "japanese": "ja",
            "CN": "zh-CN",
            "ZH": "zh-CN",
            "cn": "zh-CN",
            "zh": "zh-CN",
            "chinese": "zh-CN",
            "zh-CN": "zh-CN"
        }
        
    def _call_papago_api(self, text:str, source_language:str, target_language:str) -> str:
        headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': self._id,
        'X-Naver-Client-Secret': self._secret
        }
        data = {'source': source_language, 'target': target_language, 'text': text}
        response = requests.post(self._url, json.dumps(data), headers=headers)
        result = response.json()['message']['result']['translatedText']
        
        return result
    
    def translate_script(self, script: pd.DataFrame, source_language: str, target_language: str, save_dir=None) -> pd.DataFrame:
        if not source_language in script.keys().tolist():
            raise ValueError(f"No source language [{source_language}] in script")
        
        
        translated_script = script.copy()
        # add new column for target language
        translated_script[target_language] = pd.Series()
       
        for idx, row in script.iterrows():
            source_text = row[source_language]
            translated_text = self._call_papago_api(source_text, source_language, target_language)
            translated_script.iloc[idx, -1] = translated_text

        if save_dir is not None:
            translated_script.to_csv(save_dir+"/script.csv", index=False)
            
        return translated_script