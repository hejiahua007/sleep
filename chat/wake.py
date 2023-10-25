import pvporcupine
import pyaudio
import struct
import pyttsx3
import keyboard

porcupine_key = "cinmq/v7vHEzd3vrbTD9I24KiGgxbmUBXjxCcgG8kGnx8l48h57L6g=="
porcupine_model = 'hello-chat_en_windows_v2_2_0.ppn'

def keyword_wake_up():
    porcupine = pvporcupine.create(access_key=porcupine_key, keyword_paths=[porcupine_model])
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
    print("等待唤醒中,唤醒词:hello chat...")
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(_pcm)
        if keyword_index >= 0:
            print("唤醒了捏！")
            engine = pyttsx3.init()
            engine.say("唤醒了捏")
            engine.runAndWait()
            break
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    kws_audio.terminate()

def press_key_wake_up():
    print("按任意键唤醒...")
    keyboard.read_event()
    print("唤醒了捏！")
    engine = pyttsx3.init()
    engine.say("唤醒了捏")
    engine.runAndWait()

keyword_wake_up()
