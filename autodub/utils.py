import os
import yaml
import pandas as pd
from tqdm import tqdm
from moviepy.editor import VideoFileClip,AudioClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, vfx


env_path =  './env.yaml'
with open(env_path) as f:
    env = yaml.full_load(f)

def split_video_to_clips(input_video_path:str|os.PathLike, script:pd.DataFrame, name:str) -> None:
    '''
    Split the video into short clips based on the script and save it
    
    Parameters:
        input_video_path ('str' or 'os.PathLike'): Path to video
        
        script (pd.DataFrame): 
            Script containing time data of each line. 
            Might be generated from 'autodub.stt.STT.get_script_from_video()'
             
        name('str'): To make result dirs
    '''
    if name is None:
        name = "results/" + input_video_path.split('/')[-1].split('.')[0]
    
    video_clip_dir = f"./results/{name}/video/source/"
    audio_clip_dir = f"./results/{name}/audio/source/"
    os.makedirs(video_clip_dir, exist_ok=True)
    os.makedirs(audio_clip_dir, exist_ok=True)
    
    video_file = VideoFileClip(input_video_path)
    audio_file = video_file.audio

    with VideoFileClip(input_video_path) as video_file:
        audio_file = video_file.audio
        for idx in tqdm(range(script.shape[0]), desc="Extracting clips.."):
            start = script.iloc[idx]['start'] / 1000
            end = script.iloc[idx]['end'] / 1000
            assert start < end
            if idx + 1 >= script.shape[0]: 
                # In the last index, 'next_start' is end of the video
                next_start = None 
            else:
                next_start = script.iloc[idx+1]['start'] / 1000
                assert end <= next_start
            audio_path = audio_clip_dir + f'/segment_{str(idx).zfill(6)}.wav'
            video_path = video_clip_dir + f'/segment_{str(idx).zfill(6)}.mp4'
            
            
            # extact video clip
            video_clip = video_file.subclip(start, next_start)
            video_clip.write_videofile(video_path, verbose=False, logger=None)

            # extract audio clip
            audio_clip = audio_file.subclip(start, end)
            audio_clip.write_audiofile(audio_path, verbose=False, logger=None)
            
            prev_end = end
    return 

def merge_clips_to_video(script:pd.DataFrame, name:str, language:str):
    '''
    Merge the clips into a complete video with audio of given language
    
    Parameters:
    
        script (pd.DataFrame): 
            Script containing time data of each line. 
            Might be generated from 'autodub.stt.STT.get_script_from_video()'
             
        name('str'): To get result dirs
        
        langauge ('str') :
            Target language of output video. One of ['KO', 'EN', 'JA', 'CN'].
            Will load and merge audio-clip files from f"./results/{name}/audio/{language}/"
    '''
    output_path = f"./results/{name}/[{language}]_{name}.mp4"
    
    video_dir = f"./results/{name}/video/source/"
    audio_dir = f"./results/{name}/audio/{language}/"

    output_video = []
    for idx in tqdm(range(script.shape[0]), desc="Merging clips.."):
        video_path = video_dir + f"segment_{str(idx).zfill(6)}.mp4"
        audio_path = audio_dir + f"segment_{str(idx).zfill(6)}.wav"
        
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        
        if video_clip.duration < audio_clip.duration:
            speed_multiplier = video_clip.duration / audio_clip.duration
            video_clip = video_clip.fx(vfx.speedx, speed_multiplier)
        
        elif video_clip.duration > audio_clip.duration:
            silent = AudioClip(
                make_frame=lambda t: 0,
                duration = video_clip.duration - audio_clip.duration
                )
            audio_clip = concatenate_audioclips([audio_clip, silent])
            
        output_video.append(video_clip.set_audio(audio_clip).copy())
    output_video = concatenate_videoclips(output_video)
    
    print("Saving results..")
    output_video.write_videofile(output_path, verbose=False, logger=None)
    output_video.close()
    print(f' Successfully Saved - [ {output_path} ]')
    