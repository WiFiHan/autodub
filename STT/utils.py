import cv2
from papago_translate import translate
import os
from pydub import AudioSegment


def extract_trans_audio(input_video_path, from_lang, to_lang, result_dict):
  
  audio = AudioSegment.from_file(input_video_path)
  translated_text_sequence = []
  seg_count = 0

  prev_end = 0
  total_end = video_length(input_video_path)

  for segment in result_dict['segments']:
    start, end = segment['start'], segment['end']
    
    if prev_end < start:
      seg_count += 1
      segment_audio = extract_audio_seg(prev_end, start, audio, input_video_path, seg_count)           
      translated_text_sequence.append((prev_end, start, '', segment_audio))
    
    text = segment['text']
    translated_text = translate(text, from_lang, to_lang)
    seg_count += 1
    segment_audio = extract_audio_seg(start, end, audio, input_video_path, seg_count)           
    translated_text_sequence.append((start, end, translated_text, segment_audio))
    
    prev_end = end
  
  if prev_end < total_end:
    seg_count += 1
    segment_audio = extract_audio_seg(prev_end, total_end, audio, input_video_path, seg_count)
    translated_text_sequence.append((prev_end, total_end, '', segment_audio))
  
  return translated_text_sequence    


def extract_audio_seg(start, end, audio, input_video_path, seg_count):
    '''
    Extract audio from audio variable
    While Saving it to the file
    '''
    audio_seg = audio[start:end]
    # We have to save audio segment to a new file
    # Not implemented yet

    return audio_seg

def extract_subclips(input_video, time_segment, clip_order):
    
    #Not completed yet

    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame = time_segment[0]
    end_frame = time_segment[1]

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frames = []
    while cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    # Write frames to a new video file
    output_file = f"{input_video}_segment_{clip_order}.mp4"
    out = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*'mp4v'), fps, (frames[0].shape[1], frames[0].shape[0]))
    for frame in frames:
        out.write(frame)
    out.release()
    cap.release()

def video_length(input_video):
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    total_time = int(total_frames / fps * 1000)
    return total_time