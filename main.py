from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time, re
import random
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
import requests
from io import BytesIO
import cv2
import imageio
import numpy as np

class Login(object):
    def __init__(self):
        option = webdriver.ChromeOptions()
        #option.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(service=Service(), options= option)
        #self.browser.set_window_size(1440, 900)
        self.browser.get('https://ssfw.gdcourts.gov.cn/web/loginA?action=lawyer_login')
        time.sleep(1)
        self.input()

    def input(self):
        username='18273737153'
        password='gongjian2023'
        username_input = self.browser.find_element(By.ID, 'login_lawyer_name')
        password_input = self.browser.find_element(By.ID, 'login_lawyer_psw')
        time.sleep(1)
        ActionChains(self.browser).click(username_input)
        time.sleep(1)
        username_input.send_keys(username)
        time.sleep(1)
        ActionChains(self.browser).click(password_input)
        time.sleep(1)
        #password_input.send_keys(username)
        ActionChains(self.browser).send_keys_to_element(password_input, password).perform()
        time.sleep(1)

        ActionChains(self.browser).click(self.browser.find_element(By.CLASS_NAME, 'yidun_slider')).perform()
        time.sleep(1)
        # 获取图片地址和位置坐标列表
        self.get_offset()
        ActionChains(self.browser).key_down(Keys.CONTROL).send_keys("t").key_up(Keys.CONTROL).perform()

    def get_offset(self):
        bgImg_url = self.browser.find_element(By.CLASS_NAME, 'yidun_bg-img').get_attribute('src')
        cutImg_url = self.browser.find_element(By.CLASS_NAME, 'yidun_jigsaw').get_attribute('src')
        #读取图片
        bgImg = self.get_image(bgImg_url)
        cutImg = self.get_image(cutImg_url)
        #识别图片边缘
        bg_edge = cv2.Canny(bgImg, 100, 200)
        cut_edge = cv2.Canny(cutImg, 100, 200)
        #变色
        bgPic = cv2.colorChange(bg_edge, cv2.COLOR_GRAY2BGR)
        cutPic = cv2.colorChange(cut_edge, cv2.COLOR_GRAY2BGR)
        #缺口匹配
        res = cv2.matchTemplate(bgPic, cutPic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 寻找最优匹配
        print('坐标:'+max_val)

    def get_image(self, url):
        img = cv2.imread(url)
        if img is None:
            tmp = imageio.mimread(url)
            if tmp is not None:
                tmp = np.array(tmp)
                img = tmp[0][:,:,:3]
        return img
                
    # 计算距离
    def get_offset_distance(self, cut_image, full_image):
        for x in range(cut_image.width):
            for y in range(cut_image.height):
                cpx = cut_image.getpixel((x, y))
                fpx = full_image.getpixel((x, y))
                if not self.is_similar_color(cpx, fpx):
                    img = cut_image.crop((x, y, x + 50, y + 40))
                    # 保存一下计算出来位置图片，看看是不是缺口部分
                    img.save("1.jpg")
                    return x

    # 开始移动
    def start_move(self, distance):
        element = self.driver.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')

        # 这里就是根据移动进行调试，计算出来的位置不是百分百正确的，加上一点偏移
        distance -= element.size.get('width') / 2
        distance += 15

        # 按下鼠标左键
        ActionChains(self.driver).click_and_hold(element).perform()
        time.sleep(0.5)
        while distance > 0:
            if distance > 10:
                # 如果距离大于10，就让他移动快一点
                span = random.randint(5, 8)
            else:
                # 快到缺口了，就移动慢一点
                span = random.randint(2, 3)
            ActionChains(self.driver).move_by_offset(span, 0).perform()
            distance -= span
            time.sleep(random.randint(10, 50) / 100)

        ActionChains(self.driver).move_by_offset(distance, 1).perform()
        # ActionChains(self.driver).release(on_element=element).perform()
# czdc对的 

login = Login()

