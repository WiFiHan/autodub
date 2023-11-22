import cv2
from papago_translate import translate
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import time


def extract_trans_audio(input_video_path, from_lang, to_lang, result_dict, is_video_slice_audio):
  
  #for audio slicing
  audio = AudioSegment.from_file(input_video_path)
  seg_count = 0  
  
  #for audio output directory
  input_video_name = input_video_path.split('/')[-1].split('.')[0]
  current_time = time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))
  input_video_name = f'{input_video_name}_{current_time}'
  if not os.path.exists(f'./STT/output/{input_video_name}'):
      os.makedirs(f'./STT/output/{input_video_name}')
  if not os.path.exists(f'./STT/output/{input_video_name}/audio'):
      os.makedirs(f'./STT/output/{input_video_name}/audio')
  if not os.path.exists(f'./STT/output/{input_video_name}/video'):
      os.makedirs(f'./STT/output/{input_video_name}/video')
  output_dir = f'./STT/output/{input_video_name}'

  #for sliced translation
  translated_text_sequence = []
  prev_end = 0
  total_end = video_length(input_video_path)

  #for video slicing
  if is_video_slice_audio:
    muted_audio = AudioSegment.silent(duration=len(audio))
    video_with_no_audio = VideoFileClip(input_video_path).set_audio(muted_audio)
    input_video_path = f'{output_dir}/video_with_no_audio.mp4'
    video_with_no_audio.write_videofile(input_video_path, codec="libx264", audio_codec="aac")

  #audio, translation slicing is executed together in this loop
  for segment in result_dict['segments']:
    start, end = segment['start'], segment['end']
    
    if prev_end < start:
      seg_count += 1
      segment_audio = extract_audio_seg(prev_end, start, audio, output_dir, seg_count)           
      extract_subclips(input_video_path, output_dir, (prev_end, start), seg_count)
      translated_text_sequence.append((prev_end, start, '', segment_audio))
    
    text = segment['text']
    translated_text = translate(text, from_lang, to_lang)
    seg_count += 1
    segment_audio = extract_audio_seg(start, end, audio, output_dir, seg_count)
    print(f'{start} ~ {end}')
    extract_subclips(input_video_path, output_dir, (start, end), seg_count)
    translated_text_sequence.append((start, end, translated_text, segment_audio))
    
    prev_end = end
  
  if prev_end < total_end:
    seg_count += 1
    segment_audio = extract_audio_seg(prev_end, total_end, audio, output_dir, seg_count)
    extract_subclips(input_video_path, output_dir, (prev_end, total_end), seg_count)
    translated_text_sequence.append((prev_end, total_end, '', segment_audio))
  
  return translated_text_sequence    


def extract_audio_seg(start, end, audio, output_dir, seg_count):
    '''
    Extract audio from audio variable
    While Saving it to the file
    '''
    audio_seg = audio[start:end]
    # export path: output/input_video_name_with_time/audio/segment_{seg_count}.wav
    print(f'extracting {seg_count} audio: {len(audio_seg)}')
    output_path = f'{output_dir}/audio/segment_{seg_count}.wav'
    audio_seg.export(output_path, format='wav')

    return audio_seg

def extract_subclips(input_video, output_dir, time_segment, seg_count):
    
    cap = cv2.VideoCapture(input_video)
    fps = cap.get(cv2.CAP_PROP_FPS)

    start_frame = int(time_segment[0] / 1000 * fps)
    end_frame = int(time_segment[1] / 1000 * fps)

    cap.set(cv2.CAP_PROP_POS_FRAMES, float(start_frame))
    frames = []
    while cap.get(cv2.CAP_PROP_POS_FRAMES) <= end_frame:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    print(f'extracting {seg_count} video: {len(frames)}')

    # Write frames to a new video file
    output_file = f"{output_dir}/video/segment_{seg_count}.mp4"
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