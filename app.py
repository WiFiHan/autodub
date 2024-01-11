import os
import warnings
warnings.filterwarnings("ignore")
import argparse
import pandas as pd
import gradio as gr
from autodub import preload_models, load_stt, load_translator
from autodub.utils import sep_noise_speech, enhance_audio, prepare_clips, merge_clips_to_video, extract_audio_from_video, add_background_noise
from autodub.tts import prepare_prompts, generate_translated_speech
from autodub.script import load_script_from_json

lang2id = {
    'English': 'en',
    'Korean': NotImplementedError(), #'ko',
    "Japanese": 'ja',
    'Chinese': 'zh',
}

title_md = '''## **Autodub** - Tobig's 20th Conference
<a href="https://github.com/WiFiHan/autodub">[Github]</a> <a href="http://www.datamarket.kr/xe/">[Tobig's]</a>
'''

def process(input_video, title, stt_type, translator_type, source_language, target_language, progress=gr.Progress(track_tqdm=True)):
    source_langid = lang2id[source_language]
    target_langid = lang2id[target_language]
    
    os.makedirs(f"./results/{title}/", exist_ok=True)
    os.makedirs(f"./results/{title}/audio/", exist_ok=True)
    script_path = f"./results/{title}/script.json"
    without_noise_output_path = f"./results/{title}/[{target_langid}]_{title}.mp4"
    with_noise_output_path = f"./results/{title}/[{target_langid}]_{title}_with_noise.mp4"
    
    #Extract audio from video first
    extract_audio_from_video(input_video, f"./results/{title}/audio/init_source.wav")
    #Enhance audio
    enhance_audio(f"./results/{title}/audio/init_source.wav", f"./results/{title}/audio/source.wav")
    #Separate speech and noise for gaining noise
    sep_noise_speech(title)


    print(f'input_video is {input_video}. app.py line 41')
    # STT
    if stt_type == 'None':
        script = load_script_from_json(script_path)
    else:
        stt = load_stt(stt_type)
        script = stt.make_script_from_video(
            video_path=input_video, 
            language=source_langid, 
            title=title)
        script.to_json(script_path)
    
    # Translation
    if translator_type != 'None':
        translator = load_translator(translator_type)
        script = translator.translate_script(script, target_langid)
        script.to_json(script_path)
    
    # Extract clips
    prepare_clips(script)
    
    # Make prompts for VALL-E
    prepare_prompts(script)
    
    # Generate speech with target language
    generate_translated_speech(script, target_language=target_langid)
    
    # Merge clips
    merge_clips_to_video(script, language=target_langid)
    return without_noise_output_path

    # Merge noise and video
    # add_background_noise(without_noise_output_path, f"./results/{title}/audio/init_source_Instruments.wav", with_noise_output_path)
    # return with_noise_output_path

def reset():
    return None

demo = gr.Blocks()
with demo:
    gr.Markdown(title_md)
    with gr.Row():
        with gr.Column():
            input_video = gr.Video(label="Upload")
            title_textbox = gr.Textbox(
                label='Title',
                info="If you have uploaded the same video before, write the same title.",
                )
            STT_dropdown = gr.Radio(
                label="STT method", 
                choices=["CLOVA", "WHISPER", "None"],
                info='CHOOSE "None" If you have made script for same video before. (To save resources)'
                )
            Translator_dropdown = gr.Radio(
                label="Translation method",
                choices=["PAPAGO", "DEEPL", "None"],
                info='CHOOSE "None" If you have translated script for same video & language before (To save resources)'
                )
            source_lang_dropdown = gr.Radio(
                label="Source Language", 
                choices=["English", "Korean", "Japanese", "Chinese"],
                info="Korean - not available yet."
                )
            target_lang_dropdown = gr.Radio(
                label="Target Language",
                choices=["English", "Korean", "Japanese", "Chinese"],
                info="Korean - not available yet."
                )
            run_button = gr.Button(label="Run")
        with gr.Column():
            output_video = gr.Video(label="Result", interactive=False)

    input_video.change(fn=reset,
                       outputs=output_video)
    
    run_button.click(fn=process,
                     inputs=[
                         input_video, 
                         title_textbox,
                         STT_dropdown,
                         Translator_dropdown,
                         source_lang_dropdown,
                         target_lang_dropdown,
                         ],
                     outputs=[output_video]
                     )
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tobigs-19 Vision Conference")
    parser.add_argument('--public',action='store_true')
    args = parser.parse_args()
    
    preload_models()
    demo.queue().launch(share=args.public)