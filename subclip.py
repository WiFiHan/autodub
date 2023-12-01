import os
import time
import cv2
import pandas as pd
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from utils import video_length


def split_video_to_clips(input_video_path:str, script:pd.DataFrame, save_dir:str|None =None):
    if save_dir is None:
        save_dir = "results/" + input_video_path.split('/')[-1].split('.')[0]
    os.makedirs(save_dir + "/audio", exist_ok=True)
    os.makedirs(save_dir + "/video", exist_ok=True)
    
    audio_file = AudioSegment.from_file(input_video_path)
    video_file = VideoFileClip(input_video_path).without_audio()

    prev_end = 0
    total_end = video_length(input_video_path)
    
    for idx, row in script.iterrows():
        start, end = row['start'], row['end']
        audio_path = f'{save_dir}/audio/segment_{str(idx).zfill(6)}.wav'
        video_path = f'{save_dir}/video/segment_{str(idx).zfill(6)}.mp4'
        
        if prev_end > start:
            raise AssertionError(f"In idx {idx}: 'end' must be smaller than next 'start'.")
        
        extract_audio_seg(audio_file, start, end, audio_path)
        extract_video_seg(video_file, start, end, video_path)
        
    return 


def extract_video_seg(video_file:VideoFileClip, start:int, end:int, save_path:str) -> None:
    clip = video_file.subclip(start/1000, end/1000)
    clip.write_videofile(save_path, verbose=False, logger=None)
    return 


def extract_audio_seg(audio_file: AudioSegment, start:int, end:int, save_path:str) -> None:
    '''
    Extract audio of the given interval and save it
    '''
    audio_segment = audio_file[start:end]
    audio_segment.export(save_path, format='wav')
    
    return


def merge_clips_to_video():
    # TODO
    return NotImplementedError()