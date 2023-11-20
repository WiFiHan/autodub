import gradio as gr

title_md = '''## **Autodub** - Tobig's 20th Conference
<a href="https://github.com/WiFiHan/autodub">[Github]</a> <a href="http://www.datamarket.kr/xe/">[Tobig's]</a>
'''

def process(input_video, STT_type):
    # TODO
    if STT_type == "CLOVA":
        return input_video
    else:
        return input_video

def reset():
    return None

demo = gr.Blocks()
with demo:
    gr.Markdown(title_md)
    with gr.Row():
        with gr.Column():
            input_video = gr.Video(label="Upload")
            STT_dropdown = gr.Dropdown(["CLOVA"])
            run_button = gr.Button(label="Run")
        with gr.Column():
            output_video = gr.Video(label="Result", interactive=False)

    input_video.change(fn=reset,
                       outputs=output_video)
    
    run_button.click(fn=process,
                     inputs=[input_video, STT_dropdown],
                     outputs=output_video)
    
    
if __name__ == "__main__":
    demo.launch()