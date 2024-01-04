import os
from abc import abstractmethod
import json
import requests
import pandas as pd
from .utils import env
from .script import MultilingualScript


class Translator:
    @abstractmethod
    def translate_text(self, source_text:str, source_language:str, target_language:str) -> str:
        """
        Translate 'source_text' from 'source_language' to 'target_language'
        """
        pass
        
    def translate_script(self, 
                         script:MultilingualScript, 
                         target_language:str) -> MultilingualScript:
        """
        1. Translate each lines in the script
        2. Add translations to given script instance.
        
        Parameters:
            script ('autodub.script.MultilingualScript'): 
                MultilingualScript instance with source data
                
            target_language ('str'): 
                Target language to translate. One of ['KO', 'EN', 'JA', 'CN'].
            
        Returns:
            'autodub.script.MultilingualScript':
                Return the given script back, with new 'target_language' added.
        """
        translations = []
        
        # 1.Translate each lines in the script
        for idx, row in script.data.iterrows():
            # translate each sentence
            source_text = row['source']
            translations.append(self.translate_text(
                source_text, 
                script.source_language, 
                target_language
                ))

        # 2.Add translations to given script instance.
        script.data[target_language] = translations
        return script
    

class PapagoTranslator(Translator):
    def __init__(self):
        '''
        You must prepare "ID" & "SECERET" from your own PAPAGO account
        Follow 'https://developers.naver.com/docs/papago/papago-nmt-overview.md'
        And put them into './env.yaml'
        
        PAPAGO API Reference:
            'https://developers.naver.com/docs/papago/papago-nmt-api-reference.md'
        '''
        # PAPAGO Client ID
        self._id = env['PAPAGO']['ID']
        # PAPAGO Client Secret
        self._secret =  env['PAPAGO']['SECRET']
        self._url = 'https://openapi.naver.com/v1/papago/n2mt'
        self._get_papago_langid = {
            "ko": 'ko',
            'en': 'en',
            'ja': 'ja',
            'zh': 'zh-CN'
        }

    def translate_text(self, source_text:str, source_language:str, target_language:str) -> str:
        return self._call_papago_api(source_text, source_language, target_language)
    
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

class DeepLTranslator(Translator):
    def __init__(self):
        '''
        You must prepare "AUTH_KEY" from your own DeepL account
        Follow 'https://www.deepl.com/docs-api/translating-text/request/'
        And put them into './env.yaml'
        
        DeepL API Reference:
            'https://www.deepl.com/docs-api/translating-text/request/'
        '''
        # DeepL API Auth Key
        self._auth_key = env['DEEPL']['AUTH_KEY']
        self._url = 'https://api-free.deepl.com/v2/translate'
        self._get_deepl_langid = {
            "ko": 'KO',
            'en': 'EN',
            'ja': 'JA',
            'zh': 'ZH'
        }

    def translate_text(self, source_text:str, source_language:str, target_language:str) -> str:
        return self._call_deepl_api(source_text, source_language, target_language)
    
    def _call_deepl_api(self, text:str, source_language:str, target_language:str) -> str:
        source_langid = self._get_deepl_langid[source_language]
        target_langid = self._get_deepl_langid[target_language]
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'auth_key': self._auth_key,
            'text': text,
            'source_lang': source_langid,
            'target_lang': target_langid,
        }
        response = requests.post(self._url, data=data, headers=headers).json()
        
        if not 'translations' in response.keys():
            print(response)
            raise AssertionError()
        else:
            result = response['translations'][0]['text']
            
        return result    
    
def load_translator(name:'str') -> Translator:
    '''
    Instansiate one of 'Translator' classes
    
    Parameters:
        name ('str'): Target class. One of ['CLOVA', ...]
        
    Returns:
        'Translator': Target 'Translator' instance
    '''
    match name:
        case "PAPAGO": return PapagoTranslator()
        case "DEEPL": return DeepLTranslator()
        case _: raise ValueError()