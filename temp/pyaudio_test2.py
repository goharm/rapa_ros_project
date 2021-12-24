#!pip install SpeechRecognition

import speech_recognition as sr

# microphone에서 auido source를 생성합니다
r = sr.Recognizer()
with sr.Microphone() as source:
    print("터틀봇에게 이야기를 해주세요~")
    audio = r.listen(source)

# 구글 웹 음성 API로 인식하기 (하루에 제한 50회)
try:
    print("Google Speech Recognition thinks you said : " + r.recognize_google(audio, language='ko'))
except sr.UnknownValueError:
    print("터틀봇이 알아듣지 못했습니다.")
except sr.RequestError as e:
    print("알 수 없는 문제가 발생했습니다.; {0}".format(e))


