import json
import time
import cv2
import tesserocr
import base64
import os
from PIL import Image
from selenium import webdriver
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import tensorflow

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Referer': 'https://nsa.ntue.edu.tw/',
}

user_agent = UserAgent()
random_user_agent = user_agent.random

options = webdriver.ChromeOptions()
options.add_argument(f'user-agent={random_user_agent}')
options.add_argument('--headless') #使瀏覽器在後台運行
# options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument("--window-size=1920,1080")
# options.add_argument('--start-maximized')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-browser-side-navigation')
options.add_argument('--disable-infobars')
options.add_argument('--disable-popup-blocking')

# 禁用自動重定向
download_path = "C:\\vscode\python\.VScode\hi"  # 請指定下載路徑
prefs = {"download.default_directory":download_path}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)



def download(user_account,user_password):
    print(user_account)
    if user_account == "" or user_password == "":
        return "none"
    else:
        while True:
            driver = webdriver.Chrome(options=options)
            driver.get("https://nsa.ntue.edu.tw/") # 更改網址以前往不同網頁

            driver.implicitly_wait(10)

            # 點擊 account
            account = driver.find_element(By.ID, "account")
            account.send_keys(user_account)

            # 點擊 Password
            password = driver.find_element(By.ID, "password")
            password.send_keys(user_password)


            img_base64 = driver.execute_script("""
                var ele = arguments[0];
                var cnv = document.createElement('canvas');
                cnv.width = 160 ; cnv.height = 46;
                cnv.getContext('2d').drawImage(ele, 0, 0);
                return cnv.toDataURL('image/jpeg').substring(22);    
                """, driver.find_element(By.ID,"ImgCaptcha"))
            with open(user_account+"input.png", 'wb') as image:
                image.write(base64.b64decode(img_base64))
            

            # 處理影像
            img = Image.open(user_account+"input.png")
            (w, h) = img.size

            new_img = img.resize((int(w*4), int(h*4)))
            new_img.save(user_account+"input.png")

            img = cv2.imread(user_account+'input.png',cv2.IMREAD_GRAYSCALE) 
            _,img_bin= cv2.threshold(img,170,255,cv2.THRESH_BINARY) 
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(7,7))
            img_dilate = cv2.dilate(img_bin,kernel,iterations=1) 
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(9,9))
            img_erode = cv2.erode(img_dilate,kernel,iterations=1) 
            cv2.imwrite(user_account+"output.png",img_erode )

            #圖片轉文字
            image = Image.open(user_account+'output.png')
            result = tesserocr.image_to_text(image)
            result = result.replace(" ",'')
            result = result.replace(".",'')
            result = result.replace("-",'')
            result = result.replace("_",'')
            result = result.replace("O",'0')
            result = result.replace("D",'0')
            result = result.replace("B",'8')
            result = result.replace("b",'6')
            result = result.replace("l",'1')
            result = result.replace("i",'1')
            image.close()

            # 點擊 captcha
            captcha= driver.find_element(By.XPATH,"/html/body/div[3]/div/div[3]/div[2]/form/div[3]/input")
            captcha.send_keys(result)
            try:
                text = driver.find_element(By.XPATH,'//*[@id="swal2-content"]')
                if len(text.text) == 33 or len(text.text) == 10 :
                    print("密碼錯誤")
                    correct_password = False
                    return "none"
            except:
                print("密碼正確")
            time.sleep(1)
            # hello
            if  driver.current_url== "https://nsa.ntue.edu.tw/home":
                break
            driver.get("https://nsa.ntue.edu.tw/") 

        # 前往目標網址
        driver.get("https://nsa.ntue.edu.tw/b04/b04250")


        # 設定year和semester以更改至當學年度
        year = "112"
        semester="上學期"

        menu = driver.find_element(By.XPATH ,'//*[@id="nav-tabContent"]/div[1]/div[1]/div/div[1]/div[2]/div/button')
        menu.click()
        input_menu= driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[1]/div[1]/div/div[1]/div[2]/div/div/div[1]/input')
        input_menu.send_keys(year)
        input_menu.send_keys(Keys.ENTER)
        menu2 = driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[1]/div[1]/div/div[2]/div[2]/div/button')
        time.sleep(1)
        menu2.click()
        if semester=="上學期":
            input_menu= driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[2]/ul/li[1]/a')
            input_menu.click()
        else :
            input_menu= driver.find_element(By.XPATH,'//*[@id="nav-tabContent"]/div[1]/div[1]/div/div[2]/div[2]/div/div/div[2]/ul/li[2]/a')
            input_menu.click()
        # 點擊「科目」的下拉式選單
        i=0
        while True:
            try:
                a = '//*[@id="row_'+str(i)+'"]/td[4]'
                lesson = driver.find_element(By.XPATH ,a)
                i += 1
            except Exception as e:
                break
        st ="big5"
        st2 = "utf-8"
        time.sleep(1)
        f2 = open(user_account+".json", 'w')
        f2.write(r'{"'+user_account+'":[')
        for j in range(i):
            a = '//*[@id="row_'+str(j)+'"]/td[4]'
            lesson = driver.find_element(By.XPATH ,a)
            lessonText = lesson.text.encode(st)

            a = '//*[@id="row_'+str(j)+'"]/td[8]'
            teacher = driver.find_element(By.XPATH ,a)
            teacherText = teacher.text.encode(st)

            a = '//*[@id="row_'+str(j)+'"]/td[9]'
            lessonTime = driver.find_element(By.XPATH ,a)
            lessonTimeText = lessonTime.text.encode(st)

            a = '//*[@id="row_'+str(j)+'"]/td[10]'
            lessonClass = driver.find_element(By.XPATH ,a)
            lessonClassText = lessonClass.text

            a = {
                "lesson": lessonText.decode(st),
                "teacher": teacherText.decode(st),
                "lessonTime": lessonTimeText.decode(st),
                "lessonClass": lessonClassText
            }
            b = json.dumps(a, ensure_ascii=False).encode(st2)  # 加上 ensure_ascii=False 避免中文字出現亂碼，轉換為 UTF-8 格式的 bytes
            if j != i-1:
                f2.write(b.decode()+",")  # 寫入前再轉回 str
            else:
                f2.write(b.decode())  # 寫入前再轉回 str
        f2.write(r"]}") 
        f2.close()
        f3 = open(user_account+".json", 'r')
        information=f3.read()
        f3.close()


        # 刪除檔案
        try:
            os.remove(user_account+".json")
            os.remove(user_account+"input.png")
            os.remove(user_account+"output.png")
        except(FileNotFoundError):
            print("檔案不存在")

        return information