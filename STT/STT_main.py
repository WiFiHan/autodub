from clova_TTS import ClovaSpeechClient
from utils import extract_trans_audio
import os
import json
from pydub import AudioSegment

#input_video_path: When using relative path, be sure you know your current directory
# script_directory = os.path.dirname(os.path.abspath(__file__)) #script_directory: ./STT
# input_video_path = os.path.join(script_directory, 'data', 'media.mp4')
input_video_path = './STT/data/media.mp4'

#You may have to change this path to your own path
#You can also use URL of which mp3 file is directly uploaded
from_lang = 'ko'
to_lang = 'en' 
#You will translate 'from_lang' text to 'to_lang' text
#'ko', 'en', 'zh-CN', 'ja' are available

save_path = os.path.join(os.getcwd(), 'STT/data/media.mp4')
#make default save path
#you can change this path to your own path

is_video_slice_audio = False
#If you want to slice video with original audio, set this True

if __name__ == '__main__':

    '''
    #To execute STT, you must have env.yaml file in root directory: autodub/env_yaml
    #There you write down your own CLOVA and PAPAGO API keys
    #CLOVA API key: Console -> Clova Speech -> Service Builder: refer to https://console.ncloud.com/nest/domain
    #PAPAGO API key: Naver Developer Center -> My Application: refer to https://developers.naver.com/apps
    '''

    #CLOVA TTS: input_video_path -> json file with text and timestamp
    res = ClovaSpeechClient().req_upload(file=input_video_path, completion='sync')
    result_json = res.text
    result_dict = json.loads(result_json)

    #PAPAGO Translate: json file with text and timestamp -> json file with translated text and timestamp
    #Before translating, timestamp should be filled
    #After the function below, we gain sequence of (start, end, translated_text, audio)
    trans_audio_pairs = extract_trans_audio(input_video_path, from_lang, to_lang, result_dict)

    print(trans_audio_pairs)

