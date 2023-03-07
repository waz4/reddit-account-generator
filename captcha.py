import sys
import os
from twocaptcha import TwoCaptcha

def solveRecaptcha(sitekey, url):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    api_key = os.getenv('APIKEY_2CAPTCHA', '2b75efcbe6855b6b1ec22f205eafa0d8')

    solver = TwoCaptcha(api_key)
    result = "test"
    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)
    except Exception as e:
        print(e)

    return result
