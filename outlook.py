from seleniumwire import webdriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
import os
import sys
import random
import requests
import base64
import time
import csv
def create_driver_with_proxy(proxy_host, proxy_port, proxy_username, proxy_password):
    # Set up Selenium-Wire options for the proxy
    proxy_options = {
        'proxy': {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'https': f'https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1',  # Add any addresses you don't want to proxy
        }
    }
    options = ChromeOptions()
    # add ca.crt to chrome options
    options.add_argument('--ignore-certificate-errors-spki-list')
    options.add_argument('--ignore-ssl-errors-spki-list')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    driver = uc.Chrome(options=options, seleniumwire_options=proxy_options)
    return driver

def solve_funcaptcha(driver):
    print(f'[{bot_number}] Solving FunCaptcha...')
    time.sleep(5)
    # wait for the fun captcha iframe with id ='enforcementFrame'
    iframe0 = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#enforcementFrame'))
    )
    src_link = iframe0.get_attribute('src')
    parts = src_link.split('/')
    publickey= parts[3]
    driver.switch_to.frame(iframe0)
    time.sleep(5)
    # wait for the iframe with title="Verification challenge"
    iframe1 = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="Verification challenge"]'))
    )
    driver.switch_to.frame(iframe1)
    # wait for the iframe with id-'game-core-frame'
    iframe2 = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe#game-core-frame'))
    )
    
    driver.switch_to.frame(iframe2)
    time.sleep(5)
    # get button with text 'Next'
    next_button = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Next"]'))
    )
    next_button.click()
    time.sleep(5)
    
    def solver_challange():
        time.sleep(5)
        # get all images in iframe
        images = WebDriverWait(driver, 60).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'img'))
        )
        image = images[1]
        image_style = image.get_attribute('style') 
        image_style_split = image_style.split('"')
        blob_url = image_style_split[1]
        # get paragraph with id="key-frame-text"
        key_frame_text = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p#key-frame-text'))
        )
        question_hint = key_frame_text.text
        if 'Match this angle' in question_hint:
            question = '3d_rollball_animals'
        elif 'icon and hand direction' in question_hint:
            question = '3d_rollball_animals_multi'
        
        print(f'[{bot_number}] Challange Type: {question}')
        # get span with role="text"
        text_span = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'span[role="text"]'))
        )
        # get inner text of span
        question_text = text_span.text

        # JavaScript code to convert the blob URL to base64 and return it
        script = f'''
        const blobUrl = '{blob_url}';

        function convertBlobToBase64(blobUrl) {{
            return new Promise((resolve, reject) => {{
                const xhr = new XMLHttpRequest();
                xhr.responseType = 'blob';

                xhr.onload = function () {{
                    const reader = new FileReader();
                    reader.onloadend = function () {{
                        resolve(reader.result.split(',')[1]);
                    }};
                    reader.readAsDataURL(xhr.response);
                }};

                xhr.onerror = function () {{
                    reject(new Error('Failed to fetch the blob.'));
                }};

                xhr.open('GET', blobUrl);
                xhr.send();
            }});
        }}

        // Execute the function and return the result
        return convertBlobToBase64(blobUrl)
            .then(base64Data => {{
                return base64Data;
            }})
            .catch(error => {{
                return error.message;
            }});
        '''

        # Execute the JavaScript code and capture the result in the 'baseimg' variable
        baseimg = driver.execute_script(script)
        url = driver.current_url
        # API endpoint URL
        url = "https://api.capsolver.com/createTask"

        # Request headers
        headers = {
            "Content-Type": "application/json"
        }

        # Request payload
        payload = {
        "clientKey" : "CAP-FA66C2F9DC93028DB315DF3C6460A738",
            "task":
                {
                    "type": "FunCaptchaClassification",
                    "websiteURL":f"{url}",
                    "websitePublicKey":f"{publickey}",
                    "images": [
                        f"{baseimg}"
                    ],
                    "question": f"{question}"
                }          
        }

        response = requests.post(url, json=payload, headers=headers)

        errstatus = response.json()['errorId']
        if errstatus == 0:
            solution = response.json()['solution']['objects']
            option = solution[0]
            print(option)

        # get anchor with aria-label="Navigate to next image"
        next_image_anchor = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label="Navigate to next image"]'))
        )
        for i in range(option):
            next_image_anchor.click()
            time.sleep(0.2)
        # get the button with text 'Submit'
        submit_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//button[text()="Submit"]'))
        )
        submit_button.click()
        print(f'[{bot_number}] Challange Solved')
    
    challange_count = 0
    print(f'[{bot_number}] Waiting for Challange')
    
    while True:
        try:
            submit_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[text()="Submit"]'))
            )
            if submit_button:
                print(f'[{bot_number}] Challange Found')
                driver.save_screenshot(f'{random.randint(1000,10000)}.png')
                solver_challange()
                challange_count += 1
                continue
        except:
            print(f'[{bot_number}] No Challange Found')
            print(f'[{bot_number}] Challange Count: {challange_count}')
            print(f'[{bot_number}] Captcha Solved')
            break
            
            
            
            
    
    


if __name__ == '__main__':
    index = 9
    batch_size = 1
    # index = int(sys.argv[1])
    # batch_size = int(sys.argv[2])
    cycle_number = index + 1
    bot_number = (cycle_number % batch_size) + 1
    try:
        print(f'[{bot_number}] Starting Bot...')
        with open('names.txt', 'r') as f:
            names = f.read().splitlines()
        
        first_name = names[random.randint(0, len(names)-1)]
        last_name = names[random.randint(0, len(names)-1)]
        
        username = first_name.lower() + "_" + last_name.lower() + "_" + str(random.randint(1432, 863549))
        print(f'[{bot_number}] Username: {username}@outlook.com')
        # create strong password with max length of 10 except commas
        password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+=-') for i in range(10))
        print(f'[{bot_number}] Password: {password}')
        with open('proxies.txt', 'r') as f:
            proxies = f.read().splitlines()
            proxy = proxies[index]
            proxy_host, proxy_port, proxy_username, proxy_password = proxy.split(':')
        
        print(f'[{bot_number}] Using Proxy: {proxy}')
        driver = create_driver_with_proxy(proxy_host, proxy_port, proxy_username, proxy_password)
        
        
        driver.get('https://login.live.com/')
        # time.sleep(1200)
        time.sleep(10)
        signup_anchor = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a#signup'))
        )
        signup_anchor.click()
        time.sleep(5)
        # wait for an anchor with id="liveSwitch"
        get_new_email_anchor = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a#liveSwitch'))
        )
        get_new_email_anchor.click()
        time.sleep(5)
        # get input with id="MemberName"
        newemail_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#MemberName'))
        )
        newemail_input.send_keys(username)
        # 
        # 
        # 
        # Reserved for changing email domai!!!!!
        # 
        # 
        # 
        # 
        
        # click on button with id="iSignupAction"
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#iSignupAction'))
        )
        next_button.click()
        time.sleep(5)
        # get input with id="PasswordInput"
        password_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#PasswordInput'))
        )
        password_input.send_keys(password)
        
        # click on button with id="iSignupAction"
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#iSignupAction'))
        )
        print(f'[{bot_number}] Full Namme = {first_name} {last_name}')
        next_button.click()
        time.sleep(5)
        # get input with id="FirstName"
        firstname_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#FirstName'))
        )
        firstname_input.send_keys(first_name)
        # get input with id="LastName"
        lastname_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#LastName'))
        )
        lastname_input.send_keys(last_name)
        
        # click on button with id="iSignupAction"
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#iSignupAction'))
        )
        next_button.click()
        time.sleep(5)
        
        # get dropdown with class="datepart0 form-control win-dropdown" and select a random value
        datepart0_dropdown = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.datepart0.form-control.win-dropdown'))
        )
        datepart0_dropdown.click()
        for i in range(random.randint(1, 11)):
            datepart0_dropdown.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.2)
        datepart0_dropdown.send_keys(Keys.ENTER)
        
        # get dropdown with class="datepart1 form-control win-dropdown" and select a random value
        datepart1_dropdown = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'select.datepart1.form-control.win-dropdown'))
        )
        datepart1_dropdown.click()
        for i in range(random.randint(1, 28)):
            datepart1_dropdown.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.2)
        datepart1_dropdown.send_keys(Keys.ENTER)
        
        # get input with id="BirthYear"
        birthyear_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#BirthYear'))
        )
        birthyear_input.send_keys(random.randint(1965, 2003))
        
        # click on button with id="iSignupAction"
        next_button = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input#iSignupAction'))
        )
        next_button.click()
        time.sleep(5)

        solve_funcaptcha(driver)
        print(f'[{bot_number}] Setting Account...')
        while True:
            time.sleep(30)
            driver.save_screenshot(f'{bot_number}.png')
            url = driver.current_url
            if 'privacynotice' in url:
                continue_span = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '//span[text()="Continue"]'))
                )
                continue_span.click()
                continue
            else:
                break
        print(f'[{bot_number}] Account Ready to Use')
        driver.quit()
    
    except Exception as e:
        print(f'[{bot_number}] Error: {e}')
        driver.quit()
        sys.exit()
        
    # check the account file
    account_file = os.path.isfile('accounts.csv')
    if not account_file:
        with open('accounts.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password', 'first_name', 'last_name'])
    
    with open('accounts.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([username, password, first_name, last_name])
    
    print(f'[{bot_number}] Account Saved')
         