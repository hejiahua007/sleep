import wake
import wav_recognize
import speaking
import chat
import translate
if __name__ == '__main__':
    language = 1
    chat.tmp_prompt = chat.prompt_jan
    while 1:
        if wake.keyword_wake_up() == 1:
            print("打开识别")
            user_word = wav_recognize.listen()
            print("打印所识别到的：",user_word)
            if '说中文' in user_word:
                language = 0
                chat.tmp_prompt = chat.prompt_ch
                speaking.speak("好的，主人！", language)
                continue
            elif '说日语' in user_word:
                language = 1
                chat.tmp_prompt = chat.prompt_jan
                speaking.speak("はい、ご主人様です!", language)
                continue
            if language == 0:
                chatword = chat.chat(user_word, chat.tmp_prompt)
                print("打印chat的返回：", chatword)
                speaking.speak(chatword, language)
            else:
                user_word = translate.text2text_translate(user_word,"youdao","zh-CHS","ja")#将用户讲的中文翻译成日文
                print("打印翻译后的用户的话语：",user_word)
                chatword = chat.chat(user_word, chat.tmp_prompt)#发送日文给gpt，获得日文回答
                print("打印chat的回答：", chatword)  # 打印日文
                speaking.speak(chatword,language)#合成日文语音
                chatword = translate.text2text_translate(chatword,"youdao","ja","zh-CHS")#将用户讲的日文翻译成中文
                print("打印chat回答的翻译：",chatword)#打印日文的翻译