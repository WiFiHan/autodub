import os
import json
import requests
import pandas as pd
from .utils import env

class Translator:
    def translate_script(self, script:pd.DataFrame, source_language:str, target_language:str) -> pd.DataFrame:
        """
        Translate each lines in the script.
        
        Parameters:
            script ('pd.DataFrame'): 
                Script containing time data of each line. 
                Might be generated from 'autodub.stt.STT.get_script_from_video()'
                
            source_language ('str'):
                Source langauge in script. One of ['KO', 'EN', 'JA', 'CN'].
                
            target_language ('str'): 
                Target language to translate. One of ['KO', 'EN', 'JA', 'CN'].
            
        Returns
            'pd.DataFrame': Script with target language added
        """
        raise NotImplementedError()


class PapagoTranslator(Translator):
    def __init__(self):
        '''
        You must prepare "ID" & "SECERET" from your own PAPAGO account
        Follow 'https://developers.naver.com/docs/papago/papago-nmt-overview.md'
        And put them into 'autodub/env.yaml'
        
        PAPAGO API Reference:
            'https://developers.naver.com/docs/papago/papago-nmt-api-reference.md'
        '''
        # PAPAGO Client ID
        self._id = env['PAPAGO']['ID']
        # PAPAGO Client Secret
        self._secret =  env['PAPAGO']['SECRET']
        self._url = env['PAPAGO']['URL']
        self._get_papago_langid = {
            "ko": 'ko',
            'en': 'en',
            'ja': 'ja',
            'zh': 'zh-CN'
        }

    def _call_papago_api(self, text:str, source_language:str, target_language:str) -> str:
        source_langid = self._get_papago_langid[source_language]
        target_langid = self._get_papago_langid[target_language]
        
        headers = {
        'Content-Type': 'application/json',
        'X-Naver-Client-Id': self._id,
        'X-Naver-Client-Secret': self._secret
        }
        data = {'source': source_langid, 'target': target_langid, 'text': text}
        response = requests.post(self._url, json.dumps(data), headers=headers).json()
        
        if not 'message' in response.keys():
            print(response)
            raise AssertionError()
        else:
            result = response['message']['result']['translatedText']
            
        return result
    
    def translate_script(self, script:pd.DataFrame, source_language:str, target_language:str) -> pd.DataFrame:
        translated_script = script.copy()
        translated_texts = []
       
        for idx, row in script.iterrows():
            # translate each sentence
            source_text = row['source']
            translated_texts.append(self._call_papago_api(source_text, source_language, target_language))

        # add new column for target language
        translated_script[target_language] = translated_texts
        
        return translated_script
    

def load_translator(name:'str') -> Translator:
    '''
    Instansiate one of autodub.translator classes
    
    Parameters:
        name ('str'): Target class. One of ['CLOVA', 'WHISPER', ...]
        
    Returns:
        'Translator': Target 'Translator' instance
    '''
    match name:
        case "PAPAGO": return PapagoTranslator()
        case _: raise ValueError()