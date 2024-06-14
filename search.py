from pickle import FALSE, TRUE
import time
import numpy as np
import cv2
import chardet
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from datetime import datetime, timedelta
from keras.models import load_model
from PIL import Image
from preprocessBatch import preprocessing
import math
import re
new_url = ""
WIDTH = 140
HEIGHT = 48
allowedChars = '234579ACFHKMNPQRTYZ'
print('model loading...')
model = load_model("model.hdf5")
print('loading completed')

def start_hsr():
    #time interval
    def time_interval(times):
        # Define the time format
        time_format = "%H:%M:%S"

        # Convert the input time string to a datetime object, using today's date
        input_time = datetime.combine(datetime.today(), datetime.strptime(times, time_format).time())

        # Get the current time rounded down to the nearest half-hour
        current_time = datetime.now()
        current_time = current_time.replace(second=0, microsecond=0)

        if current_time.time() >= datetime.strptime("00:30:00", time_format).time() and current_time.time() < datetime.strptime("05:00:00", time_format).time():
            current_time = current_time.replace(hour=5, minute=0)

        # Calculate the minutes portion of the input time
        minutes = current_time.minute

        # Round the minutes to the nearest half-hour
        if minutes < 15:
            current_time = current_time.replace(minute=0)
        elif minutes < 45:
            current_time = current_time.replace(minute=30)
        else:
            # Round up to the next hour
            current_time = current_time.replace(minute=0, hour=current_time.hour + 1)


        minutes = input_time.minute
        if minutes < 30:
            input_time = input_time.replace(minute=0)
        elif minutes < 60:
            input_time = input_time.replace(minute=30)

        # Calculate the time difference between the rounded current time and the input time
        time_difference = input_time - current_time

        if time_difference.total_seconds() <= 0:
            input_time += timedelta(hours=24)
            time_difference = input_time - current_time
        # Calculate the number of 30-minute intervals
        intervals = math.ceil(time_difference.total_seconds() / 1800)
        print(input_time)
        print(current_time)
        print(time_difference)
        print(intervals)
        return intervals

    def date_interval(date):
        # Parse the cleaned date string into a datetime object
        date_object = datetime.strptime(date, "%d-%m-%Y")

        # Calculate the difference in days
        current_date = datetime.now()
        date_difference = date_object - current_date
        days_until_ticket = date_difference.days
        return days_until_ticket

    variables = {}  # Create an empty dictionary to store the variables

    # Function to detect file encoding
    def detect_encoding(file_path):
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']

    # Function to open file and handle decoding issues
    def open_file(file_path, encoding='utf-8'):
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:
            content = file.readlines()
        return content

    # Detect encoding of result.txt
    file_encoding = detect_encoding('result.txt')

    # Open the file with the detected encoding
    file_content = open_file('result.txt', encoding=file_encoding)

    for line in file_content:
        # Your processing logic for each line
        try:
            key, value = line.strip().split(': ')
            variables[key] = value
        except ValueError as e:
            print(f"Error processing line: {line}. {e}")
            # Handle the error as needed, e.g., skip the line or log it

    # Now, you can access the variables like this:
    from_location = variables.get('From')
    to_location = variables.get('To')
    trip = variables.get('Trip')
    date = variables.get('Date')
    times = variables.get('Time')
    discount = variables.get('Discount')

    print(f'From: {from_location}')
    print(f'To: {to_location}')
    print(f'Trip: {trip}')
    print(f'Date: {date}')
    print(f'Time: {times}')
    print(f'Discount: {discount}')

    t_interval = time_interval(times)
    d_interval = date_interval(date)

    if trip == "去回程":
        r_date = variables.get('Return Date')
        r_time = variables.get('Return Time')
        print(f'Return Date: {r_date}')
        print(f'Return Time: {r_time}') 
        r_date_interval = date_interval(r_date)
        r_time_interval = time_interval(r_time)

    current_attempt = 1
    while True:
        try:
            options = webdriver.FirefoxOptions()
            #options.add_argument("--disable-automation")
            #options.add_argument("--disable-blink-features=AutomationControlled")        
            #options.add_argument('--disable-gpu')
            
            driver = webdriver.Firefox(options=options)
            #driver.get("https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/querybytime")
            #driver.get("https://irs.thsrc.com.tw/IMINT/?Locale=tw")
            #driver.get("https://irs.thsrc.com.tw/IMINT/?locale=tw&info=U1cwMjA1MDgyNTIwMjMxMjI0MjAyMzExMjcxNTQxMzQxMjYz")
            driver.get("https://www.thsrc.com.tw")
            # Clear the browser cache
            driver.execute_script("localStorage.clear();")
            driver.execute_script("sessionStorage.clear();")
            driver.execute_script("window.location.reload(true);")


            #bootstrap-datetimepicker-widget.dropdown-menu.usetwentyfour.top
            print(driver.title)
            print(driver.current_url)
            #input("Press Enter to continue...")
            #同意
            wait = WebDriverWait(driver, 10)
            click_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "swal2-confirm.swal2-styled")))
            click_button.click()
            #時刻表與票價
            element = driver.find_element(by=By.XPATH,value="/html/body/div[4]/div[3]/div/section[1]/div/div[2]/ul/li[1]/a")
            element.click()

            dropdownbox = Select(driver.find_element(by=By.ID,value="select_location01"))
            dropdownbox.select_by_visible_text(from_location)
            dropdownbox = Select(driver.find_element(by=By.ID,value="select_location02"))
            dropdownbox.select_by_visible_text(to_location)
            dropdownbox = Select(driver.find_element(by=By.ID,value="typesofticket"))
            if trip == '去回程':
                dropdownbox.select_by_visible_text('去回程')
                drop_text = '去回程'
            else:
                dropdownbox.select_by_visible_text('單程')
                drop_text = '單程'

            button = driver.find_element(by=By.CLASS_NAME, value = "btn.dropdown-toggle.btn-light.bs-placeholder").click()
            #早鳥
            if discount == '早鳥':
                discount = driver.find_element(by=By.XPATH, value = "/html/body/div[4]/div[3]/div/section[1]/div/div[3]/div[1]/div/div[4]/div/div/div/ul/li[1]/a").click()
            #校外教學
            if discount == '校外教學':
                discount = driver.find_element(by=By.XPATH, value = "/html/body/div[4]/div[3]/div/section[1]/div/div[3]/div[1]/div/div[4]/div/div/div/ul/li[2]/a").click()
            #大學生
            if discount == '大學生':
                discount = driver.find_element(by=By.XPATH, value = "/html/body/div[4]/div[3]/div/section[1]/div/div[3]/div[1]/div/div[4]/div/div/div/ul/li[3]/a").click()
            #20人團體
            if discount == '20人團體':
                discount = driver.find_element(by=By.XPATH, value = "/html/body/div[4]/div[3]/div/section[1]/div/div[3]/div[1]/div/div[4]/div/div/div/ul/li[4]/a").click()
            #企業會員團體
            if discount == '企業會員團體':
                discount = driver.find_element(by=By.XPATH, value = "/html/body/div[4]/div[3]/div/section[1]/div/div[3]/div[1]/div/div[4]/div/div/div/ul/li[5]/a").click()
            # 42 days
            #One-Way Date
            date = driver.find_element(by=By.ID, value = "Departdate01")
            date.click()
            i = 0
            while i <= d_interval:
                date.send_keys(Keys.ARROW_RIGHT)
                i += 1
            #One-Way Time
            date_time = driver.find_element(by=By.ID, value = "outWardTime")
            date_time.click()
            i = 0
            while i < t_interval:
                date_time.send_keys(Keys.ARROW_UP)
                i += 1

            if (drop_text == "去回程"):
                #Return Date
                date_return = driver.find_element(by=By.ID, value = "Returndate01")
                date_return.click()
                i = 0
                while i <= r_date_interval:
                    date_return.send_keys(Keys.ARROW_RIGHT)
                    i += 1
                #Return Time
                date_time_return = driver.find_element(by=By.ID, value = "returnTime")
                date_time_return.click()
                i = 0
                while i < r_time_interval:
                    date_time_return.send_keys(Keys.ARROW_UP)
                    i += 1

            #start
            start = driver.find_element(by=By.ID, value = "start-search").click()

            #TIME
            ########################################################################
            # Outgoing Times
            parent_element_1 = wait.until(EC.presence_of_element_located((By.ID, "timeTableTrain_S")))
            elements_1 = parent_element_1.find_elements(By.CLASS_NAME, "tr-row")

            # Return Times (only if trip is "去回程")
            elements_2 = []
            if trip == "去回程":
                parent_element_2 = wait.until(EC.presence_of_element_located((By.ID, "timeTableTrain_R")))
                elements_2 = parent_element_2.find_elements(By.CLASS_NAME, "tr-row")

            all_elements = elements_1 + elements_2
            # Initialize lists to store extracted times
            outgoing_times = []
            return_times = []

            # Iterate through the elements and extract the time
            for element in all_elements:
                time_element = element.find_element(By.CLASS_NAME, "font-16r.darkgray")
                text = time_element.text
                # Check if it's an empty string (this usually means a new group of times is starting)
                if text != "":
                    if element in elements_1:
                        outgoing_times.append(text)
                    elif element in elements_2:
                        return_times.append(text)

            # Print the extracted times
            print("Outgoing Times:")
            for t in outgoing_times:
                print(t)

            print("-" * 30)

            if trip == "去回程":
                print("Return Times:")
                for t in return_times:
                    print(t)

            nearest_bigger_time = None
            min_time_difference = float('inf')
            nearest_bigger_index = -1
            given_time = datetime.strptime(times, "%H:%M:%S")
            # Iterate through the outgoing times and find the nearest bigger time
            for index, outgoing_time in enumerate(outgoing_times):
                outgoing_time = datetime.strptime(outgoing_time, "%H:%M")
                time_difference = (outgoing_time - given_time).total_seconds()

                if time_difference > 0 and time_difference < min_time_difference:
                    min_time_difference = time_difference
                    nearest_bigger_time = outgoing_time
                    nearest_bigger_index = index
            if nearest_bigger_time:
                print("Outgoing Time:", nearest_bigger_time.strftime("%H:%M"))
                #print("Index:", nearest_bigger_index)
            else:
                print("No nearest bigger time found.")
            index_1 = nearest_bigger_index
            if trip == "去回程":                
                nearest_bigger_time = None
                min_time_difference = float('inf')
                nearest_bigger_index = -1
                given_time = datetime.strptime(r_time, "%H:%M:%S")
                # Iterate through the outgoing times and find the nearest bigger time
                for index, return_time in enumerate(return_times):
                    return_time = datetime.strptime(return_time, "%H:%M")
                    time_difference = (return_time - given_time).total_seconds()

                    if time_difference > 0 and time_difference < min_time_difference:
                        min_time_difference = time_difference
                        nearest_bigger_time = return_time
                        nearest_bigger_index = index
                if nearest_bigger_time:
                    print("Return Time:", nearest_bigger_time.strftime("%H:%M"))
                    #print("Index:", nearest_bigger_index)
                else:
                    print("No nearest bigger time found.")
                index_2 = nearest_bigger_index
            ########################################################################
            #Second Page
            element_to_click_1 = elements_1[index_1]
            element_to_click_1.click()

            if trip == "去回程":
                
                head = driver.find_elements(By.CLASS_NAME, "tr-nav-head")
                element_to_click_2 = elements_2[index_2]
                driver.execute_script("arguments[0].scrollIntoView(true);", head[1])
                element_to_click_2.click()

            # Wait for the web to load, then click the table
            go = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "order")))
            go.click()
            
                # You can add more logging or debugging information here

            ########################################################################
            #Third Page
            time.sleep(3)
            #delay time

            driver.switch_to.window(driver.window_handles[1])
            #switch to new tab
            agree = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "cookieAccpetBtn"))
            )
            agree.click()

            captcha_element = driver.find_element(by=By.ID, value = "BookingS1Form_homeCaptcha_passCode")
            new_url = driver.current_url
            print(new_url)
            captcha_element = driver.find_element(by=By.ID, value="BookingS1Form_homeCaptcha_passCode")
            # Capture a screenshot of the CAPTCHA element
            captcha_element.screenshot('captcha.png')
            img = Image.open('captcha.png')
            img = img.resize((WIDTH, HEIGHT), Image.ANTIALIAS)
            img = img.convert('RGB')
            img.save('resized_captcha.jpg', "JPEG")
            preprocessing('resized_captcha.jpg', 'preprocessing.jpg')
            train_data = np.stack([np.array(cv2.imread("preprocessing.jpg")) / 255.0])
            prediction = model.predict(train_data)
            predict_captcha = ''
            for predict in prediction:
                value = np.argmax(predict[0])
                predict_captcha += allowedChars[value]
            #captchaInput = driver.find_element(By.ID, "securityCode")
            #captchaInput.send_keys(predict_captcha)
            with open('url.txt', 'w') as file:
                file.write(new_url + '\n')
                file.write(predict_captcha + '\n')
            driver.quit()
            break
        except WebDriverException as e:
            print(f"An unexpected exception occurred: {e}")
            current_attempt += 1
            #break
            driver.quit()
            if True:
                print(f"Retrying... Attempt {current_attempt}")
