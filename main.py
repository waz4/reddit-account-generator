# Reddit account generator
# notes:
#   - 1 account every 10mn per IP
from os.path import exists
import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from accountCredentialGenerator import randomPassword, randomUsername
from captcha import solveRecaptcha

# this option is needed so that the browser dosent close after the script is finished, usefull for debugging
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
# chrome_options.add_argument('--headless')

def generateAccount():
    status = 0 #Account generated status
    error = "" #Account generatiion Error

    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(30)
    wait = WebDriverWait(driver,10)

    registerUrl = "https://www.reddit.com/register/"
    driver.get(registerUrl)

    # generate credential
    email = ""
    username = randomUsername()
    password = randomPassword(8)

    #fill in email field 
    emailField = driver.find_element(By.ID, "regEmail")
    emailField.send_keys(email)

    continueButton = driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/div[2]/form/fieldset[3]/button")
    continueButton.click()

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
    except TimeoutError as e:
        print("g-recaptcha-response not found")
        raise e
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
    logLine = f"{TimeStamp}|{email}|{username}|{password}"

    if email == "":
        email = "NOEMAIL"

    if(status != 1):
        outputFile = f"errors{outputFile}"
        logLine += f"|{error}"
    
    if(not exists(f"output/{outputFile}")):
        writeHeader(outputFile, TimeStamp)

    with open(f"output/{outputFile}", 'a') as f:
        f.write(logLine + "\n")

def writeHeader(outputFile, Timestamp):
    header = f"----- HEADER START -----\nAccounts created on {Timestamp}\nData is structured in the following format:\nTimeStamp|Email|Username|Password\n----- HEADER CLOSE -----"
    with open(f"output/{outputFile}", 'w') as f:
        f.write(header + "\n")

#generate Accounts every X amount of seconds
def main(outputFile: str, generationInterval: int = 605):
    successFullAccountsCounter = 0
    failedAccountsCounter = 0
    try:
        while(True):
            print("Generating New Account")
            status, email, username, password, error = generateAccount()
            # status, email, username, password, error = (1, "darren@gmail.com", "darren", "password", "")
            log(outputFile, status, email, username, password, error) 

            if(status == 1):
                print("Success")
                successFullAccountsCounter += 1
            else: 
                print("Failed")
                print(error)
                failedAccountsCounter += 1

            sleep(generationInterval) #wait 10 minutes and 5 seconds until next iteration
    except KeyboardInterrupt:
        print("Finished")
main("account.txt")