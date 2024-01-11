import os
import yaml
import pandas as pd
from tqdm import tqdm
from moviepy.editor import VideoFileClip,AudioClip, AudioFileClip, concatenate_videoclips, concatenate_audioclips, vfx
from .script import MultilingualScript

env_path =  './env.yaml'
with open(env_path) as f:
    env = yaml.full_load(f)

def prepare_clips(script:MultilingualScript) -> None:
    '''
    Split the video into short clips based on the script and save it
    
    Parameters:
        script('MultilingualScript): 
            A 'MultilingualScript' containing timestamp data of each lines.
    '''
    
    videoClip_dir = script.output_dir + "/video/source"
    audioClip_dir = script.output_dir + "/audio/source/"
    os.makedirs(videoClip_dir, exist_ok=True)
    os.makedirs(audioClip_dir, exist_ok=True)
    
    video_source = VideoFileClip(script.source_path)
    audio_source = video_source.audio

    for idx in tqdm(range(len(script)), desc="Extracting clips.."):
        # 1. get timestamp
        start = script.data.iloc[idx]['start'] / 1000
        end = script.data.iloc[idx]['end'] / 1000
        assert start < end
        if idx + 1 >= len(script): 
            # Set 'next_start' to end of the video when it's last index.
            next_start = None 
        else:
            next_start = script.data.iloc[idx+1]['start'] / 1000
            assert end <= next_start
            
        audioClip_path = audioClip_dir + f'/segment_{str(idx).zfill(6)}.wav'
        videoClip_path = videoClip_dir + f'/segment_{str(idx).zfill(6)}.mp4'
        
        # 2. extact video clip
        videoClip = video_source.subclip(start, next_start)
        videoClip.write_videofile(videoClip_path, verbose=False, logger=None)

        # 3. extract audio clip
        audioClip = audio_source.subclip(start, end)
        audioClip.write_audiofile(audioClip_path, verbose=False, logger=None)
        
        prev_end = end
    return 

def merge_clips_to_video(script:MultilingualScript, language:str):
    '''
    Merge the clips into a complete video with audio of given language
    
    Parameters:
        script ('autodub.script.MultilingualScript'):
            To get timestamp data.
            
        langauge ('str') :
            Target language of output video. One of ['KO', 'EN', 'JA', 'CN'].
            Audio-clip files in f"{script.output_dir}/audio/{language}/" will be merged.
    '''
    output_path = script.output_dir + f"[{language}]_{script.title}.mp4"
    
    videoClip_dir = script.output_dir + f"/video/source/"
    audioClip_dir = script.output_dir + f"/audio/{language}/"

    output_video = []
    for idx in tqdm(range(len(script)), desc="Merging clips.."):
        videoClip_path = videoClip_dir + f"segment_{str(idx).zfill(6)}.mp4"
        audioClip_path = audioClip_dir + f"segment_{str(idx).zfill(6)}.wav"
        
        videoClip = VideoFileClip(videoClip_path)
        audioClip = AudioFileClip(audioClip_path)
        
        # Match the length of audio and video
        if videoClip.duration < audioClip.duration:
            # If audioClip is longer than videoClip, slow down the videoClip
            speed_multiplier = videoClip.duration / audioClip.duration
            videoClip = videoClip.fx(vfx.speedx, speed_multiplier)
        
        elif videoClip.duration > audioClip.duration:
            # If videoClip is longer that audioClip, add a short silence at the end of audioClip.
            silent = AudioClip(
                make_frame=lambda t: 0,
                duration = videoClip.duration - audioClip.duration
                )
            audioClip = concatenate_audioclips([audioClip, silent])
            
        output_video.append(videoClip.set_audio(audioClip).copy())
    output_video = concatenate_videoclips(output_video)
    
    print("Saving results..")
    output_video.write_videofile(output_path, verbose=False, logger=None)
    output_video.close()
    print(f' Successfully Saved - [ {output_path} ]')
    