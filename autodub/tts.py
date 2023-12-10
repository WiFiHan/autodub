import os
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.io.wavfile import write as write_wav
from .VALL_E_X.utils.prompt_making import make_prompt
from .VALL_E_X.utils.generation import SAMPLE_RATE, generate_audio
from .script import MultilingualScript



def enhance_speech(audio_clip_dir:str|os.PathLike):
    # TODO: Implement Speech Enhancement
    '''
    Enhance and replace all audio files in given dir.
    '''
    raise NotImplementedError()

def prepare_prompts(script:MultilingualScript, enhance:bool=False):
    '''
    Generate and save prompt files.
    
    Parameters:
        script ('autodub.script.MultilingualScript'): To get audioClip_dir and transcripts.

        enhance ('bool'): Whether or not to use speech enhancement
    '''
    audio_clip_dir = script.output_dir + "/audio/source/"
    prompt_dir = script.output_dir + "/prompt/"
    os.makedirs(prompt_dir, exist_ok=True)
    
    for idx, row in tqdm(script.data.iterrows(), total=len(script), desc="Generating prompts.."):
        audio_clip_path = audio_clip_dir + f"/segment_{str(idx).zfill(6)}.wav"
        prompt_path = prompt_dir + f"/prompt_{str(idx).zfill(6)}.npz"
        if enhance:
            enhance_speech(audio_clip_dir)
            
        prompt = make_prompt(
                    name=script.title,
                    audio_path=audio_clip_path,
                    transcript=row['source']
                    )
        np.savez(prompt_path, **prompt)


def generate_translated_speech(script:MultilingualScript, target_language:str):
    assert script.is_available(target_language)
    
    prompt_dir = script.output_dir + "/prompt/"
    output_dir = script.output_dir + f"/audio/{target_language}/"
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, row in tqdm(script.data.iterrows(), total=len(script), desc="Generating translated speech.."):
        prompt_path = prompt_dir + f"/prompt_{str(idx).zfill(6)}.npz"
        output_path = output_dir + f"/segment_{str(idx).zfill(6)}.wav"
        
        text = row[target_language]
        audio_array = generate_audio(text, prompt_path, language=target_language)
        write_wav(output_path, SAMPLE_RATE, audio_array)

    
