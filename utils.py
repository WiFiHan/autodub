import os
import yaml
import cv2

env_path =  './env.yaml'
with open(env_path) as f:
    env = yaml.full_load(f)

def video_length(input_video):
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = int(total_frames / fps * 1000)
    return total_time