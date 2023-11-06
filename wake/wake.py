import pvporcupine
import pyaudio
import struct
import pyttsx3
import keyboard
import speaking
import time
porcupine_key = 
porcupine_model = ''

def keyword_wake_up():
    start_time = time.time()  # 记录程序启动时间
    porcupine = pvporcupine.create(access_key=porcupine_key, keyword_paths=[porcupine_model])

    end_time = time.time()  # 记录唤醒时间
    elapsed_time = end_time - start_time
    print(f"从启动到创建porcupine的时间：{elapsed_time:.2f}秒")#从启动到创建porcupine的时间：0.50秒、0.48秒

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
    end_time = time.time()  # 记录唤醒时间
    elapsed_time = end_time - start_time
    print(f"从启动到等待唤醒的时间：{elapsed_time:.2f}秒")#开启语音流耗时0.65秒、0.24秒
    while True:
        pcm = audio_stream.read(porcupine.frame_length)
        _pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        keyword_index = porcupine.process(_pcm)
        if keyword_index :
        # if keyword_index >= 0:
            print("唤醒了捏！")
            # engine = pyttsx3.init()
            # engine.say("唤醒了捏")
            # engine.runAndWait()
            # speaking.speak("有什么事吗？主人。")#合成语音耗时1.9秒
            speaking.play_audio("../file/tmp/wake.wav")#更新
            return 1
            break
    audio_stream.stop_stream()
    audio_stream.close()
    porcupine.delete()
    kws_audio.terminate()

def press_key_wake_up():
    print("按任意键唤醒...")
    keyboard.read_event()
    print("唤醒了捏！")
    # engine = pyttsx3.init()
    # engine.say("唤醒了捏")
    # engine.runAndWait()
    speaking.speak("有什么事吗？主人。")
    return 1

keyword_wake_up()
