import os
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import gradio as gr
from autodub import preload_models, load_stt, load_translator
from autodub.utils import split_video_to_clips, merge_clips_to_video
from autodub.tts import prepare_prompts, generate_translated_speech


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
    script_path = f"./results/{title}/script.csv"
    output_path = f"./results/{title}/[{target_langid}]_{title}.mp4"
    
    # STT
    if stt_type == 'None':
        script = pd.read_csv(script_path)
    else:
        stt = load_stt(stt_type)
        script = stt.get_script_from_video(input_video, source_langid)
        script.to_csv(script_path, index=False)
    
    # Translation
    if translator_type != 'None':
        translator = load_translator(translator_type)
        script = translator.translate_script(script, source_langid, target_langid)
        script.to_csv(script_path, index=False)
    
    # Extract clips
    split_video_to_clips(input_video, script, name=title)
    
    # Make prompts for VALL-E
    prepare_prompts(script, name=title)
    
    # Generate speech with target language
    generate_translated_speech(script, name=title, target_language=target_langid)
    
    # Merge clips
    merge_clips_to_video(script, name=title, language=target_langid)
    
    return output_path

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
                choices=["CLOVA", "None"],
                info='CHOOSE "None" If you have made script for same video before. (To save resources)'
                )
            Translator_dropdown = gr.Radio(
                label="Translation method",
                choices=["PAPAGO", "None"],
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
    preload_models()
    demo.queue().launch()