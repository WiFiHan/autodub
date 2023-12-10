import os
import json
import pandas as pd


_required_keys = ['start', 'end', 'source']

class MultilingualScript:
    def __init__(self, title:str, source_path:str, source_language:str, data:pd.DataFrame):
        assert all(map(lambda x: x in data.keys().values, _required_keys))
        self.title = title  
        self.source_path = source_path
        self.source_language = source_language
        self.data = data
        
        self.output_dir = f"./results/{self.title}/"
    
    def is_available(self, language:str) -> bool:
        '''
        Return 'True' if script contains the given language data.
        '''
        return language in self.data.keys().values
    
    def to_json(self, path:str|None=None) -> None:
        if path is None:
            path = self.output_dir + "script.json"
        out = {
            "title": self.title,
            "source_path": self.source_path,
            "source_language": self.source_language,
            "data": self.data.to_dict('records')
        }
        with open(path, 'w') as f:
            json.dump(out, f, indent=4, ensure_ascii=False)
    
    def __repr__(self) -> str:
        return f'TITLE: "{self.title}"\nDATA:\n{str(self.data)}'
    
    def __len__(self) -> int:
        return self.data.shape[0]

def load_script_from_json(json_path:str) -> MultilingualScript:
    with open(json_path, 'r') as f:
        d = json.load(f)
        
    title = d['title']
    path = d['source_path']
    language = d['source_language']
    data = pd.DataFrame(d['data'])
    
    return MultilingualScript(title, path, language, data)