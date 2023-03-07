# Reddit account generator
# notes:
#   - 1 account every 10mn per IP
#TODO: make captcha API only be called once per minute at max so that I dont go broke
import datetime, concurrent.futures
from os.path import exists
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from accountCredentialGenerator import randomPassword, randomUsername
from captcha import solveRecaptcha
from getFreeWorkingProxyList import getWorkingProxyList, TARGET_URL, NUMBER_OF_THREADS


NUMBER_OF_THREADS = 16
TARGET_URL = "https://httpbin.org/ip"

chrome_options = Options()
# this option is needed so that the browser dosent close after the script is finished, usefull for debugging
# chrome_options.add_experimental_option("detach", True)
# this options hide the browser window usefull for runninga as a background process
chrome_options.add_argument('--headless')


def getNewWebDriver(proxy_ip_port: str):
    proxy = Proxy()
    proxy.proxy_type = ProxyType.MANUAL
    proxy.http_proxy = proxy_ip_port
    proxy.ssl_proxy = proxy_ip_port

    capabilities = webdriver.DesiredCapabilities.CHROME
    proxy.add_to_capabilities(capabilities)

    driver = webdriver.Chrome(options=chrome_options, desired_capabilities=capabilities) 
    driver.implicitly_wait(60)

    return driver

def generateAccount(driver):
    status = 0
    error = email = username = password = "" # initialize all variables so that it dosent crash if theres an error on the start of the function
    wait = WebDriverWait(driver,10)

    registerUrl = "https://www.reddit.com/register/"
    try:
        driver.get(registerUrl)
    except:
        error = "Failed to get webpage!"
    else:
        # generate credential
        username = randomUsername()
        password = randomPassword(8)

        #fill in email field 
        try:
            emailField = driver.find_element(By.ID, "regEmail")
            emailField.send_keys(email)
        except:
            error = "Couldnt find Email field!"
        else:
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/main/div[1]/div/div[2]/form/fieldset[2]/button")))
                continueButton = driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/div[2]/form/fieldset[2]/button")
                continueButton.click()
            except TimeoutException as e:
                error = "Failed to find continue button"
            else:
                # fill in username and password fields
                usernameField = driver.find_element(By.ID, "regUsername")
                passwordField = driver.find_element(By.ID, "regPassword")
                usernameField.send_keys(username)
                passwordField.send_keys(password)

                # solve captcha
                sitekey = "6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC"
                captchaResult = solveRecaptcha(sitekey, registerUrl)
                code = captchaResult["code"]
                # code = "success"

                try:
                    wait.until(EC.presence_of_element_located((By.ID, "g-recaptcha-response")))
                except TimeoutException as e:
                    error = "g-recaptcha-response not found"
                else:
                    driver.execute_script(
                        "document.getElementById('g-recaptcha-response').innerHTML = '{}'".format(code)
                    )

                    # press sign up button
                    signupButton = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div[3]/button")
                    signupButton.click()

                    try:
                        wait.until(EC.url_changes(registerUrl))
                    except TimeoutException as e:
                        error = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div[3]/span/span[2]").text
                    else:
                        status = 1

    return (status, email, username, password, error) 

def log(outputFile: str, status: int, email: str, username: str, password: str, error: str):
    TimeStamp = "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())

    if email == "" or email == None:
        email = "NOEMAIL"

    logLine = f"{TimeStamp}|{email}|{username}|{password}"

    if(status != 1):
        outputFile = f"errors{outputFile}"
        logLine += f"|{error}"
    
    if(not exists(f"output/{outputFile}")):
        writeHeader(outputFile, TimeStamp)

    with open(f"output/{outputFile}", 'a') as f:
        f.write(logLine + "\n")

def writeHeader(outputFile, Timestamp):
    header = f"----- HEADER START -----\nAccounts created on {Timestamp}\nData is structured in the following format:\nTimeStamp|Email|Username|Password\n----- HEADER CLOSE -----"
    with open(f"output/{outputFile}", 'w+') as f:
        f.write(header + "\n")

#generate Accounts every X amount of seconds
def main():
    proxyList = [[proxy, 0] for proxy in getWorkingProxyList()]
    print(proxyList)

    while(True):
        proxiedDrivers = map(getNewWebDriver, [proxy for proxy, lastTimeUsed in proxyList])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(generateAccount, driver) for driver in proxiedDrivers]

            for future in concurrent.futures.as_completed(futures):
                status, email, username, password, error = future.result()
                if status == 1:
                    print("Account Created Successfully!")
                log("accounts.txt", status, email, username, password, error)
        print("Generation round finished \n Going to sleep!")
        sleep(605)

main()
