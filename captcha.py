import sys
import os
from twocaptcha import TwoCaptcha

def solveRecaptcha(sitekey, url):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    api_key = os.getenv('APIKEY_2CAPTCHA', '3dddc279b7daa50f3f1437c09bac96e8')

    solver = TwoCaptcha(api_key)
    result = "test"
    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)
    except Exception as e:
        print(e)

    return result