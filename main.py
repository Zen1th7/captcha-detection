import speech_recognition as sr
import webbrowser
import re
import time as tm
from datetime import datetime, timedelta
from PIL import Image, ImageTk
from pathlib import Path
import tkinter as tk
from tkinter import Canvas, Entry, Text, Button, PhotoImage, Scrollbar, StringVar, messagebox, filedialog
from main import start_hsr

from preprocessBatch import preprocessing
import numpy as np
import cv2
from keras.models import load_model
model = load_model("model.hdf5")
allowedChars = '234579ACFHKMNPQRTYZ'

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = Path("assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

energy_th = 700

class SpeechRecognitionApp:
    def __init__(self, master):
        
        self.master = master
        self.master.title("THSRC")  # Set the title

        self.master.geometry("800x500")
        self.master.configure(bg = "#FFFFFF")


        self.canvas = Canvas(
            self.master,
            bg = "#FFFFFF",
            height = 500,
            width = 800,
            bd = 0,
            highlightthickness = 0,
            relief = "ridge"
        )
        
        self.canvas.place(x = 0, y = 0)
        self.image_image_1 = tk.PhotoImage(
            file=relative_to_assets("image_1.png"))
        self.image_1 = self.canvas.create_image(
            400.0,
            250.0,
            image=self.image_image_1
        )

        self.text_id = self.canvas.create_text(
            234.0,
            87.0,
            anchor="nw",
            text="WELCOME",
            fill="#19B87F",
            font=("Julee Regular", 80 * -1)
        )

        self.rectangle_id = self.canvas.create_rectangle(
            24.0,
            193.0,
            773.0,
            201.0,
            fill="#00FFD1",
            outline="")

        self.button_image_hsr = tk.PhotoImage(
            file=relative_to_assets("button_1.png"))
        self.button_hsr = tk.Button(
            image=self.button_image_hsr,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: self.second_page('hsr'),
            relief="flat"
        )
        self.button_hsr.place(
            x=250.0,
            y=217.0,
            width=302.0,
            height=63.0
        )
        
        # Start Search
        self.button_image_2 = tk.PhotoImage(
            file=relative_to_assets("button_2.png"))
        # Start Recording Personal Information
        self.button_image_3 = tk.PhotoImage(
            file=relative_to_assets("button_record.png"))
        self.button_image_6 = tk.PhotoImage(
            file=relative_to_assets("button_show.png"))
        # Initialize the speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = energy_th
        self.mic = sr.Microphone()

    def second_page(self, transport):
        self.transport = transport
        self.canvas.itemconfig(self.text_id, state='hidden')
        self.canvas.itemconfig(self.rectangle_id, state='hidden')
        self.button_hsr.destroy()
        

        # Create an image element on a canvas at coordinates (638.0, 129.0)

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_2.png"))
        self.entry_bg_1 = self.canvas.create_image(
            251.0,
            179.5,
            image=entry_image_1
        )
        self.entry_1 = Text(
            bd=0,
            bg="#75F6FF",
            fg="#000716",
            highlightthickness=0
        )
        self.entry_1.place(
            x=63.0,
            y=65.0,
            width=376.0,
            height=227.0
        )
        entry_image_2 = PhotoImage(
            file=relative_to_assets("entry_3.png"))
        self.entry_bg_2 = self.canvas.create_image(
            638.0,
            250.5,
            image=entry_image_2
        )
        self.entry_2 = Text(
            bd=0,
            bg="#75F6FF",
            fg="#000716",
            highlightthickness=0,
            font=("Helvetica", 40),  # Adjust the font size as needed
            wrap="word",  # Wrap text at word boundaries
            width=30
        )
        self.entry_2.place(
            x=534.0,
            y=218.0,
            width=208.0,
            height=63.0
        )


        #input("Press Enter to continue...")
        self.second_page_button()
    def second_page_button(self):
        button_image_2 = self.button_image_2  # Use the stored PhotoImage instance
        self.button_2 = tk.Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=self.start_search,
            relief="flat"
        )
        self.button_2.place(
            x=296.0,
            y=409.0,
            width=208.0,
            height=31.0
        )

        button_image_3 = self.button_image_3 
        self.start_information_button = tk.Button(
            image=button_image_3,
            borderwidth=0,
            highlightthickness=0,
            command=self.start_recording,
            relief="flat"
        )
        self.start_information_button.place(
            x=296.0,
            y=319.0,
            width=208.0,
            height=31.0
        )

        button_image_6 = self.button_image_6
        self.button_6 = tk.Button(
            image=button_image_6,
            borderwidth=0,
            highlightthickness=0,
            command=self.show_search_result,
            relief="flat"
        )
        self.button_6.place(
            x=322.0,
            y=364.0,
            width=155.0,
            height=31.0
        )
        self.upload_button = tk.Button(self.master, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(pady=20)
        self.upload_button.place(
            x=595.0,
            y=190.0,
        )
   
    def clean_date_string(self, day, month, year):
        try:
            day = int(day)
            month = int(month)
            year = int(year)

            # Check if the day and month are valid
            if 1 <= month <= 12:
                if month in [1, 3, 5, 7, 8, 10, 12]:
                    valid_days = range(1, 32)
                elif month in [4, 6, 9, 11]:
                    valid_days = range(1, 31)
                elif month == 2:
                    # Check for a leap year
                    leap_year = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                    valid_days = range(1, 30) if leap_year else range(1, 29)
                else:
                    valid_days = []

                if 1 <= day <= 31 and day in valid_days:
                    # Check if the date is not too far in the future
                    requested_date = datetime(year, month, day)
                    today = datetime.now()
                    max_allowed_date = today + timedelta(days=28)

                    if requested_date > max_allowed_date or today > requested_date:
                        available_date_range = f"{today.strftime('%Y-%m-%d')} 到 {max_allowed_date.strftime('%Y-%m-%d')}"
                        error_message = f"所選日期超出有效範圍 ({available_date_range})，請再試一次。"
                        self.print_get_information(error_message)
                        return None  # Date is too far in the future
                    
                    return f"{day}-{month}-{year}"
                else:
                    self.print_get_information("請再試一次。")
        except ValueError:
            pass

    def extract_time(self, text):
        # Use regular expression to find time information
        time_pattern = r'(\d+)點(\d+)?(分|分鐘|)?(早上|上午|下午|晚上)?'
        time_pattern2 = r'(早上|上午|下午|晚上)?(\d+)點(\d+)?(分|分鐘|)?'
        
        # Handle case where hour is a Chinese character
        chinese_hour_pattern = re.compile(r'([一二三四五六七八九十]+)點(\d+)?(分|分鐘|)?(早上|上午|下午|晚上)?')

        time_match = re.search(time_pattern, text)

        if time_match:
            hour, minute, _, period = time_match.groups()
            hour = int(hour)
            minute = int(minute) if minute else 0

            if period in ["下午", "上午"] and hour == 12:
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "晚上"] and hour == 12:
                hour = 0
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "上午"]:
                if 1 <= hour <= 11:
                    return f"{hour:02d}:{minute:02d}:00"
            elif period in ["下午", "晚上"]:
                if 1 <= hour <= 11:
                    hour += 12
                    return f"{hour:02d}:{minute:02d}:00"

        # If the first pattern didn't match, check the second pattern
        time_match2 = re.search(time_pattern2, text)
        if time_match2:
            period, hour, minute, _ = time_match2.groups()
            hour = int(hour)
            minute = int(minute) if minute else 0

            if period in ["下午", "上午"] and hour == 12:
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "晚上"] and hour == 12:
                hour = 0
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "上午"]:
                if 1 <= hour <= 11:
                    return f"{hour:02d}:{minute:02d}:00"
            elif period in ["下午", "晚上"]:
                if 1 <= hour <= 11:
                    hour += 12
                    return f"{hour:02d}:{minute:02d}:00"

        # If the second pattern didn't match, check the Chinese character pattern
        chinese_hour_match = chinese_hour_pattern.search(text)
        if chinese_hour_match:
            chinese_hour, minute, _, period = chinese_hour_match.groups()
            def convert_chinese_hour_to_arabic(chinese_hour):
                chinese_numerals = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
                if chinese_hour == '十':
                    return 10
                elif chinese_hour[-1] == '十':
                    return chinese_numerals[chinese_hour[0]] * 10
                else:
                    return chinese_numerals[chinese_hour]
            hour = convert_chinese_hour_to_arabic(chinese_hour)
            minute = int(minute) if minute else 0
            if period in ["下午", "上午"] and hour == 12:
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "晚上"] and hour == 12:
                hour = 0
                return f"{hour:02d}:{minute:02d}:00"
            elif period in ["早上", "上午"]:
                if 1 <= hour <= 11:
                    return f"{hour:02d}:{minute:02d}:00"
            elif period in ["下午", "晚上"]:
                if 1 <= hour <= 11:
                    hour += 12
                    return f"{hour:02d}:{minute:02d}:00"
        return None

    def extract_locations(self, text, valid_locations):
        words = text.split()  # Split the input text into words
        for word in words:
            if word in valid_locations:
                return word
        return None  # If no valid location is found in the text

    def is_file_empty(self, filename):
        with open(filename, 'r') as file:
            return file.read().strip() == ''
    
    def on_hyperlink_click(self, event):
        messagebox.showinfo("Hyperlink Clicked", f"You clicked the hyperlink:\n{self.new_url}")
        webbrowser.open_new(self.new_url)

    def upload_image(self):
        try:
            self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")])
        except Exception as e:
            print(f"Error opening image: {e}")
        if self.image_path:           
            self.captcha_name = PhotoImage(file=self.image_path)
            self.captcha_image = self.canvas.create_image(
                638.0,
                129.0,
                image=self.captcha_name
            )

            img = Image.open(self.image_path)
            img = img.resize((140, 48), Image.ANTIALIAS)
            img = img.convert('RGB')
            img.save('resized_captcha.jpg', "JPEG")
            preprocessing('resized_captcha.jpg', 'preprocessing.jpg')
            train_data = np.stack([np.array(cv2.imread("preprocessing.jpg")) / 255.0])
            prediction = model.predict(train_data)
            predict_captcha = ''
            for predict in prediction:
                value = np.argmax(predict[0])
                predict_captcha += allowedChars[value]
            self.entry_2.delete(1.0, tk.END) 
            self.entry_2.insert(tk.END, predict_captcha)
            self.entry_2.see(tk.END)
            self.entry_2.update_idletasks()
    
    def print_get_information(self, prompt):
        self.entry_1.insert(tk.END, prompt + "\n")
        self.entry_1.see(tk.END)
        self.entry_1.update_idletasks()
    
    def print_info(self, result):
        self.entry_1.delete(1.0, tk.END) 
        self.entry_1.insert(tk.END, result)
        self.entry_1.see(tk.END)
        self.entry_1.update_idletasks()

    def start_recording(self):
        if self.transport == "hsr":
            self.start_recording_hsr()
    def start_recording_hsr(self):
        self.entry_1.delete(1.0, tk.END)
        # Function to start the speech recognition process
        # Display prompts and recognized speech in the Tkinter window
        prompts = [
            "請告訴我出發地點：",
            "請告訴我去的地點：",
            "請告訴我單程還是去回程：",
            "請告訴我日期：",
            "請告訴我時間：",
            "請告訴我返回日期：",
            "請告訴我返回時間:",
            "請告訴我折扣：",
        ]
        from_location = to_location = trip = date = time = return_date = return_time = discount = special = ticket_q = ""

        time_prompt_index = 4  # Index of the trip type prompt in the prompts list
        i = 0
        while i < len(prompts):
            prompt = prompts[i]
            self.entry_1.insert(tk.END, prompt + "\n")

            if prompt == "請告訴我出發地點：" or prompt == "請告訴我去的地點：":
                self.entry_1.insert(tk.END, "南港, 台北, 板橋, 桃園, 新竹, 苗栗, 台中, 彰化, 雲林, 嘉義, 台南, 左營\n")
            elif prompt == "請告訴我單程還是去回程：":
                self.entry_1.insert(tk.END, "One-way or Round-trip\n")
            elif prompt == "請告訴我日期：" or prompt == "請告訴我返回日期：":
                self.entry_1.insert(tk.END, "Ex: 25號11月2023 or 25日11月2023\n")
            elif prompt == "請告訴我時間：" or prompt == "請告訴我返回時間:":
                self.entry_1.insert(tk.END, "Ex: 晚上10點10分 or 10點早上\n")
            elif prompt == '請告訴我折扣：':
                self.entry_1.insert(tk.END, "早鳥, 校外教學, 大學生, 20人團體, 企業會員團體\n")
            self.entry_1.see(tk.END)
            self.entry_1.update_idletasks()
            # Call the get_information function to get user input through speech
            result = self.get_information(prompt)
            if result == "重新開始" or result == "retry":
                self.start_recording_hsr()
                break
            if result == "stop" or result == "停":
                break
            else:
                if i == 0:
                    from_location = result
                    #from_location = "台北"
                elif i == 1:
                    to_location = result
                    #to_location = "苗栗"
                elif i == 2:
                    trip = result
                    #trip = "單程"
                elif i == 3:
                    date = result
                    #date = "23-11-2023"
                elif i == 4:
                    time = result
                    #time = "10:00:00"
                elif i == 5:
                    while True:
                        result = self.get_information(prompt)
                        if result is not None:
                            if result > date:
                                break
                            else:
                                self.entry_1.insert(tk.END, f"User Input: {result}\nReturn date should be on or after the departure date. Please try again.\n")
                                self.entry_1.see(tk.END)
                                self.entry_1.update_idletasks()
                                print("Return date should be on or after the departure date. Please try again.")
                        else:
                            self.entry_1.insert(tk.END, f"Could not recognize the date. Please try again.\n")
                            self.entry_1.see(tk.END)
                            self.entry_1.update_idletasks()
                            print("Could not recognize the date. Please try again.")
                    return_date = result
                elif i == 6:
                    return_time = result
                elif i == 7:
                    discount = result
                    #discount = "大學生"

                self.entry_1.insert(tk.END, f"User Input: {result}\n\n")
                self.entry_1.see(tk.END)
                self.entry_1.update_idletasks()  # Update the Tkinter window

                if i == time_prompt_index and trip == "單程":
                    i += 3
                elif i == 7:
                    break
                else:
                    i += 1
        

                    # Write information to a text file
        if result != "stop":
            with open('result.txt', 'w') as output_file:
                output_file.write("From: " + str(from_location) + "\n")
                output_file.write("To: " + str(to_location) + "\n")
                output_file.write("Trip: " + str(trip) + "\n")
                output_file.write("Date: " + str(date) + "\n")
                output_file.write("Time: " + str(time) + "\n")
                output_file.write("Discount: " + str(discount) + "\n")
                if trip == "去回程":
                    output_file.write("Return Date: " + str(return_date) + "\n")
                    output_file.write("Return Time: " + str(return_time) + "\n")
                
            #print("Results have been written to 'result.txt'")
    def get_information(self, prompt):
        while True:
            
            with self.mic as source:
                try:
                    #audio play
                    self.recognizer.adjust_for_ambient_noise(source)

                    audio = self.recognizer.listen(source)
                    text = self.recognizer.recognize_google(audio, language="zh-TW")
                    text = text.replace(" ", "")
                    self.print_get_information("\n" + text)
                    if text in "重新開始" or text in "retry" or text in "stop" or text in "停":
                        return text
                    # Location
                    if self.transport == "hsr":                        
                        valid_locations = ["南港", "台北", "板橋", "桃園", "新竹", "苗栗", "台中", "彰化", "雲林", "嘉義", "台南", "左營"]

                    if prompt == "請告訴我出發地點：":
                        from_location = self.extract_locations(text, valid_locations)
                        if from_location:
                            return from_location
                        else:
                            self.print_get_information("請再試一次。")
                    elif prompt == "請告訴我去的地點：":
                        to_location = self.extract_locations(text, valid_locations)
                        if to_location:
                            return to_location
                        else:
                            self.print_get_information("請再試一次。")
                    # way
                    elif prompt == "請告訴我單程還是去回程：":
                        if "roundtrip" in text or "round-trip" in text:
                            trip = "去回程"
                            return trip
                        elif "oneway" in text:
                            trip = "單程"
                            return trip
                        else: 
                            self.print_get_information("請再試一次。")
                    # date
                    elif prompt == "請告訴我日期：" or prompt == "請告訴我返回日期：":
                        date_pattern = r'(\d+)號(\d+)月(\d{4})'
                        date_pattern2 = r'(\d+)日(\d+)月(\d{4})'
                        date_match = re.search(date_pattern, text)
                        
                        if date_match is None:
                            date_match = re.search(date_pattern2, text)
                        
                        if date_match:
                            day, month, year = date_match.groups()
                            cleaned_date_string = self.clean_date_string(day, month, year)

                            if cleaned_date_string is not None:
                                return cleaned_date_string
                        else:
                            self.print_get_information("請再試一次。")
                    # time
                    elif prompt == "請告訴我時間：" or prompt == "請告訴我返回時間:":
                        time = self.extract_time(text)
                        
                        if time:
                            #print("Time:", time)
                            return time
                        else:
                            self.print_get_information("請再試一次。")
                    # Discount
                    elif prompt == '請告訴我折扣：':
                        if "沒有" in text:
                            Discount0 = "沒有"
                            return Discount0
                        if "早鳥" in text:
                            Discount1 = "早鳥"
                            return Discount1
                        if "校外教學" in text:
                            Discount2 = "校外教學"
                            return Discount2
                        if "大學生" in text:
                            Discount3 = "大學生"
                            return Discount3
                        if "20人團體" in text:
                            Discount4 = "20人團體"
                            return Discount4
                        if "企業會員團體" in text:
                            Discount5 = "企業會員團體"
                            return Discount5

                except sr.UnknownValueError:
                    #print('無法辨識您的講話。 請再試一次。')                    
                    self.print_get_information("無法辨識您的講話。 請再試一次。")
                    tm.sleep(1)
                except sr.WaitTimeoutError:
                    #print('語音辨識超時。 請再試一次。')
                    self.print_get_information("語音辨識超時。 請再試一次。")
                    tm.sleep(1)
                except sr.RequestError:
                    #print('語音服務已關閉。 請稍後再試。')
                    self.print_get_information("語音服務已關閉。 請稍後再試。")
                    tm.sleep(1)
            self.recognizer.energy_threshold = energy_th

    def show_results(self, filename):
        try:
            with open(filename, 'r') as result_file:
                result_contents = result_file.read()
            self.print_info("Please copy the Link below:")
            self.print_info(result_contents)
        except Exception as e:
            self.print_info(f"Error reading the file: {e}")
        
    def show_search_result(self):
        if self.transport == "hsr":
            self.show_results("result.txt")

    def start_search(self):
        if self.transport == "hsr":
            result_file_empty = self.is_file_empty("result.txt")

            if result_file_empty:
                self.print_info("Search Result is empty.")
                self.start_recording_hsr()
            else:
                start_hsr()
                with open('url.txt', 'r') as file:
                    content = file.readlines()

                # Now, 'content' is a list where each element corresponds to a line in the file
                # You can access the values like this:
                self.new_url = content[0].strip()  # Assuming new_url is on the first line
                predict_captcha = content[1].strip()
                self.print_info("Please copy or press the link below:\n")
                self.entry_1.tag_configure("hyperlink", foreground="blue", underline=True)

                # Insert the hyperlink text with the "hyperlink" tag
                hyperlink_text = self.new_url
                self.entry_1.insert(tk.END, hyperlink_text, "hyperlink")

                # Bind the callback function to the "hyperlink" tag
                self.entry_1.tag_bind("hyperlink", "<Button-1>", self.on_hyperlink_click)

                self.image_image_2 = PhotoImage(file="captcha.png")
                self.image_2 = self.canvas.create_image(
                    638.0,
                    129.0,
                    image=self.image_image_2
                )
                self.entry_2.delete(1.0, tk.END) 
                self.entry_2.insert(tk.END, predict_captcha)
                self.entry_2.see(tk.END)
                self.entry_2.update_idletasks()
                self.master.update_idletasks()

if __name__ == "__main__":
    window = tk.Tk()
    app = SpeechRecognitionApp(window)
    window.resizable(False, False)
    window.mainloop()
