from captcha.image import ImageCaptcha
import random

text = ""
for i in range(5):
    text += random.choice("abcdefghijklmnopqrstuvwxyz")  # ABCDEFGHIJKLMNOPQRSTUVWXYZ
ImageCaptcha(250, 100).write(text, "captcha.png")
if input() == text:
    print("correct")
