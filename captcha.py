import sys
import os
from twocaptcha import TwoCaptcha

def solveRecaptcha(sitekey, url):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

    api_key = os.getenv('APIKEY_2CAPTCHA', 'fbe96c17474fe734390e5af98ed68f87')

    solver = TwoCaptcha(api_key)
    result = "test"
    try:
        result = solver.recaptcha(
            sitekey=sitekey,
            url=url)

    except Exception as e:
        print(e)

    return result