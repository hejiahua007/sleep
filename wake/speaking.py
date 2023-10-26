import subprocess
import argparse
import torch
import time
from torch import no_grad, LongTensor
import asyncio
import utils
from models import SynthesizerTrn
from text import text_to_sequence
import commons
from scipy.io import wavfile
import pygame

#noise_scale(控制感情变化程度)
vitsNoiseScale = 0.6
#noise_scale_w(控制音素发音长度)
vitsNoiseScaleW = 0.668
#length_scale(控制整体语速)
vitsLengthScale = 1.0
_init_vits_model = False

hps_ms = None
device = None
net_g_ms = None

def play_audio(audio_file_name):
    # 初始化pygame
    pygame.init()
    # 设置音频文件
    pygame.mixer.music.load(audio_file_name)
    # 播放音频
    pygame.mixer.music.play()
    # 等待音频播放完毕
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    # 退出pygame
    pygame.quit()
# def play_audio(audio_file_name):
#     command = f'mpv.exe -vo null {audio_file_name}'
#     subprocess.run(command, shell=True)

def init_vits_model():
    # 全局变量引入
    global hps_ms, device, net_g_ms

    # 创建参数解析器
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str, default='cpu')
    parser.add_argument('--api', action="store_true", default=False)
    parser.add_argument("--share", action="store_true", default=False, help="share gradio app")
    parser.add_argument("--colab", action="store_true", default=False, help="share gradio app")
    args = parser.parse_args()
    device = torch.device(args.device)
    # 从文件中获取VITS模型的参数
    hps_ms = utils.get_hparams_from_file('config.json')
    # 创建VITS模型
    net_g_ms = SynthesizerTrn(
        len(hps_ms.symbols),
        hps_ms.data.filter_length // 2 + 1,
        hps_ms.train.segment_size // hps_ms.data.hop_length,
        n_speakers=hps_ms.data.n_speakers,
        **hps_ms.model)
    # 将VITS模型设置为评估模式，并移动到指定设备
    _ = net_g_ms.eval().to(device)
    # 获取说话者信息
    speakers = hps_ms.speakers
    # 加载模型和优化器
    model, optimizer, learning_rate, epochs = utils.load_checkpoint('../file/model/G_953000.pth', net_g_ms, None)
    # 标记VITS模型已初始化
    _init_vits_model = True

def get_text(text, hps):
    # 使用text_to_sequence将输入文本转换为模型可用的格式
    text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    # 如果需要在文本中添加空白符，则在文本序列中插入0（代表空白符）
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    # 将文本序列转换为LongTensor（长整数）格式
    text_norm = LongTensor(text_norm)
    return text_norm, clean_text

def vits(text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
    global over
    # 记录生成开始时间
    start = time.perf_counter()
    # 处理输入文本
    if not len(text):
        return "输入文本不能为空！", None, None
    text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
    if len(text) > 600:
        return f"输入文字过长！{len(text)}>300", None, None
    # 根据语言类型添加标记
    if language == 0:
        text = f"[ZH]{text}[ZH]"
    elif language == 1:
        text = f"[JA]{text}[JA]"
    else:
        text = f"{text}"
    # 调用get_text将文本转换为模型可用的格式
    stn_tst, clean_text = get_text(text, hps_ms)
    # 使用VITS模型生成音频
    with no_grad():
        x_tst = stn_tst.unsqueeze(0).to(device)
        x_tst_lengths = LongTensor([stn_tst.size(0)]).to(device)
        speaker_id = LongTensor([speaker_id]).to(device)
        audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale, noise_scale_w=noise_scale_w,
                               length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()
    # 返回生成成功信息、音频信息以及生成耗时
    return "生成成功!", (22050, audio), f"生成耗时 {round(time.perf_counter()-start, 2)} s"

async def start(input_str=None,language = 0):
    if input_str == None:
        print("请输入 >")
        input_str = await asyncio.get_event_loop().run_in_executor(None, input, '')
    if "关闭AI" in input_str:
        return
    result = input_str
    status, audios, time = vits(result,language, 124, vitsNoiseScale, vitsNoiseScaleW, vitsLengthScale)
    print("VITS : ", status, time)
    wavfile.write("../file/tmp/output.wav", audios[0], audios[1])
    play_audio("../file/tmp/output.wav")

def speak(input_str = None,language = 0):
    if not _init_vits_model:
        init_vits_model()
    if input_str != None:
        asyncio.run(start(input_str,language))

# speak()

async def main():
    if not _init_vits_model:
        init_vits_model()
    await asyncio.gather(start(),)

#asyncio.run(main())