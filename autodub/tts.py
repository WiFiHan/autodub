import os
import glob
import numpy as np
import pandas as pd
from tqdm import tqdm
from .VALL_E_X.utils.prompt_making import make_prompt
from autodub.VALL_E_X.utils.generation import SAMPLE_RATE, generate_audio
from scipy.io.wavfile import write as write_wav


def prepare_prompts(script, name):
    audio_clip_dir = f"./results/{name}/audio/source/"
    prompt_dir = f"./results/{name}/prompt/"
    os.makedirs(f"./results/{name}/prompt/source", exist_ok=True)
    
    for idx, row in tqdm(script.iterrows(), total=script.shape[0], desc="Generating prompts.."):
        audio_clip_path = audio_clip_dir + f"/segment_{str(idx).zfill(6)}.wav"
        prompt_path = prompt_dir + f"/prompt_{str(idx).zfill(6)}.npz"
        prompt = make_prompt(name=name,
                    audio_path=audio_clip_path,
                    transcript=row['source']
                    )
        np.savez(prompt_path, **prompt)


def generate_translated_speech(script:pd.DataFrame, name:str, target_language:str):
    if not target_language in script.keys():
        raise ValueError(f"target_language '{target_language}' doesn't exist in script. You should get translated script from 'autodub.translator.Translator")
    
    output_dir = f"./results/{name}/audio/{target_language}/"
    prompt_dir = f"./results/{name}/prompt/"
    os.makedirs(output_dir, exist_ok=True)
    
    for idx, row in tqdm(script.iterrows(), total=script.shape[0], desc="Generating translated speech.."):
        prompt_path = prompt_dir + f"/prompt_{str(idx).zfill(6)}.npz"
        output_path = output_dir + f"/segment_{str(idx).zfill(6)}.wav"
        
        text = row[target_language]
        audio_array = generate_audio(text, prompt_path, language=target_language)
        write_wav(output_path, SAMPLE_RATE, audio_array)

    
