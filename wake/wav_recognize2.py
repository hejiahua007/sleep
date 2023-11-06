# 腾讯云asr,输入base64编码的wav音频，输出text，此函数需异步调用，以节约请求事件
#from tencentcloud.common import credential
#from tencentcloud.common.profile.client_profile import ClientProfile
#from tencentcloud.common.profile.http_profile import HttpProfile
#from tencentcloud.asr.v20190614 import asr_client, models
from aip import AipSpeech
import struct
import pvporcupine
import pyaudio
#import asyncio
import json
import base64
import io
import wave
import pvcobra
porcupine_key = 
porcupine_model = 


def sound_record():
    porcupine = pvporcupine.create(access_key=porcupine_key, keyword_paths=[porcupine_model])
    cobra = pvcobra.create(access_key=porcupine_key)
    # 开启录音流
    kws_audio = pyaudio.PyAudio()
    audio_stream = kws_audio.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
        input_device_index=None,
    )
    # 开始录音
    frames = []
    print("开始录音...")
    silence_count = 0
    is_voiced = 1
    while is_voiced:
        pcm = audio_stream.read(porcupine.frame_length)
        _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        is_voiced = cobra.process(_pcm)
        silence_count = 0 if is_voiced > 0.5 else silence_count  + 1
        if silence_count <= 80:
            if silence_count < 10:
                frames.append(pcm)
        else:
            break
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    kws_audio.terminate()

    # 将数据帧编码为base64编码的WAV格式
    with io.BytesIO() as wav_buffer:
        with wave.open(wav_buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(kws_audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(porcupine.sample_rate)
            wf.writeframes(b''.join(frames))
        wav_base64 = base64.b64encode(
            wav_buffer.getvalue()).decode('utf-8')
        #保存的路径
        output_file = '../file/tmp/recorded_audio.wav'  # 替换成你想要保存的路径
        with open(output_file, 'wb') as output_file:
            output_file.write(base64.b64decode(wav_base64))
        print(f"录音已保存")
    return wav_base64


''' 你的APPID AK SK  参数在申请的百度云语音服务的控制台查看'''
APP_ID = 
API_KEY =
SECRET_KEY = 

# 新建一个AipSpeech
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)



def baidu_stt(wav_base64):
    wav_bytes = base64.b64decode(wav_base64)  # 将base64字符串解码为字节序列
    result = client.asr(wav_bytes, 'wav', 16000, {'dev_pid': 1536})  # 传递字节序列给client.asr

    if result['err_msg'] == 'success.':
        words = result['result'][0].encode('utf-8').decode('utf-8')  # 将结果从bytes转换为字符串
        print(words)
        with open('demo.txt', 'w', encoding='utf-8') as f:
            f.write(words)
        return words
    else:
        print("语音识别错误")
        return ""

'''
# 腾讯云api的ID和key，用于语音识别
tencent_Id = "AKIDkKsKZyBAvVr22qSpztY1FHCsNhs1zFKA"
tencent_key = "iN1PZi1Qo6AC7nGWcbOB0jT4U6lTAoMj"

async def tencent_asr(wav_base64):
    cred = credential.Credential(tencent_Id, tencent_key)
    # 实例化一个http选项，可选的，没有特殊需求可以跳过
    httpProfile = HttpProfile()
    httpProfile.endpoint = "asr.ap-guangzhou.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化要请求产品的client对象,clientProfile是可选的
    client = asr_client.AsrClient(cred, "", clientProfile)
    # 实例化一个请求对象,每个接口都会对应一个request对象
    req = models.SentenceRecognitionRequest()
    params = {
        "ProjectId": 0,
        "SubServiceType": 2,
        "EngSerViceType": "16k_zh",
        "SourceType": 1,
        "VoiceFormat": "wav",
        "UsrAudioKey": "0",
        "Data": wav_base64,  # 音频二进制数据
        "DataLen": len(wav_base64)  # 音频长度
    }
    req.from_json_string(json.dumps(params))
    response = await asyncio.to_thread(client.SentenceRecognition, req)

    if response.Result == "":
        print("你什么都没说~")
    else:
        print("你：" + response.Result)
    return response.Result
'''

def listen(model: str = "baidu"):
    audio_data = sound_record()

    if model == "tencent":
        #user_words = asyncio.run(tencent_asr(audio_data))
        print("1")
    elif model == "baidu":
        user_words = baidu_stt(audio_data)
    else:
        user_words = "Unsupported speech recognition model"

    if user_words == "":
        print("你什么都没说")
    else:
        print("你说了: ", user_words)

    return user_words


listen()
