# Reddit account generator
# notes:
#   - 1 account every 10mn per IP
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

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(30)
wait = WebDriverWait(driver,10)

registerUrl = "https://www.reddit.com/register/"
driver.get(registerUrl)

# generate credential
tempMail = ""
username = randomUsername()
password = randomPassword(8)

#fill in email field 
emailField = driver.find_element(By.ID, "regEmail")
emailField.send_keys(tempMail)

continueButton = driver.find_element(By.XPATH, "/html/body/div/main/div[1]/div/div[2]/form/fieldset[3]/button")
continueButton.click()

# fill in username and password fields
usernameField = driver.find_element(By.ID, "regUsername")
passwordField = driver.find_element(By.ID, "regPassword")
usernameField.send_keys(username)
passwordField.send_keys(password)

# solve captcha
sitekey = "6LeTnxkTAAAAAN9QEuDZRpn90WwKk_R1TRW_g-JC"
result = solveRecaptcha(sitekey, registerUrl)
code = result["code"]
# code = "success"

try:
    wait.until(EC.presence_of_element_located((By.ID, "g-recaptcha-response")))
except TimeoutError as e:
    print(e)
    print("g-recaptcha-response not found")
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
    print("Fail")
    print(driver.find_element(By.XPATH, "/html/body/div[1]/main/div[2]/div/div/div[3]/span/span[2]").text)
else:
    print("Success")
    print(username)
    print(password)
    with open('accounts.txt', 'a') as f:
        f.write("{} {}".format(username, password), "\n")