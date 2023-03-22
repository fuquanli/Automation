from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.wait import WebDriverWait
import requests
import cv2


class Login(object):

    retryCount = 1

    def __init__(self):
        option = webdriver.ChromeOptions()
        # option.add_experimental_option("detach", True)
        self.browser = webdriver.Chrome(service=Service(), options=option)
        self.browser.maximize_window()
        # self.browser.set_window_size(1440, 900)
        self.browser.get(
            'https://ssfw.gdcourts.gov.cn/web/loginA?action=lawyer_login')
        time.sleep(1)
        self.input()

    def input(self):
        # username = '18273737153'
        # password = 'gongjian2023'
        # username_input = self.browser.find_element(By.ID, 'login_lawyer_name')
        # password_input = self.browser.find_element(By.ID, 'login_lawyer_psw')
        # time.sleep(1)
        # ActionChains(self.browser).click(username_input)
        # time.sleep(1)
        # username_input.send_keys(username)
        # time.sleep(1)
        # ActionChains(self.browser).click(password_input)
        # time.sleep(1)
        # # password_input.send_keys(username)
        # ActionChains(self.browser).send_keys_to_element(
        #     password_input, password).perform()
        # time.sleep(1)

        slider = self.browser.find_element(
            By.CLASS_NAME, 'yidun_panel')  # 滑块定位

        ActionChains(self.browser).click(slider)
        time.sleep(1)

        #distance = self.get_distance()
        #track = self.get_track(distance)
        #print('滑动轨迹', track)

        self.move_to_gap(slider, 150)

        time.sleep(20)

        ActionChains(self.browser).key_down(Keys.CONTROL).send_keys(
            "t").key_up(Keys.CONTROL).perform()

    def get_distance(self):
        bg_img, tp_img = self.get_images()
        bg_edge = cv2.Canny(bg_img, 100, 200)
        tp_edge = cv2.Canny(tp_img, 100, 200)

        bg_pic = cv2.cvtColor(bg_edge, cv2.COLOR_GRAY2RGB)
        tp_pic = cv2.cvtColor(tp_edge, cv2.COLOR_GRAY2RGB)

        res = cv2.matchTemplate(bg_pic, tp_pic, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 寻找最优匹配

        print('X坐标:')
        print(max_loc[0])

        th, tw = tp_pic.shape[:2]
        tl = max_loc  # 左上角点的坐标
        br = (tl[0]+tw, tl[1]+th)  # 右下角点的坐标
        cv2.rectangle(bg_pic, tl, br, (0, 0, 255), 2)  # 绘制矩形
        cv2.imwrite('out.jpg', bg_pic)

        # 返回缺口的X坐标
        return tl[0]

    def get_track(self, distance):
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        while current < distance:                   # 所以 track是不会大于总长度的
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 移动距离x = v0t + 1/2 * a * t^2，现做了加速运动
            move = v0 * t + 1 / 2 * a * t * t
            # 当前速度v = v0 + at  速度已经达到v，该速度作为下次的初速度
            v = v0 + a * t
            # 当前位移
            current += move
            # 加入轨迹
            # track 就是最终鼠标在 X 轴移动的轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        ActionChains(self.browser).click_and_hold(
            on_element=slider).perform()         # 利用动作链，获取slider，perform是
        time.sleep(0.5)
        ActionChains(self.browser).move_by_offset(
            xoffset=150, yoffset=0).perform()
        # for x in track:
        #     print(x)
        #     ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()       # xoffset横坐标，yoffset纵坐标。使得鼠标向前推进
        #     time.sleep(0.2)
        time.sleep(10)                                     # 推动到合适位置之后，暂停一会
        #ActionChains(self.browser).release().perform()      # 抬起鼠标左键

    def get_images(self):
        bg_url = self.browser.find_element(
            By.CLASS_NAME, 'yidun_bg-img').get_attribute('src')
        tg_url = self.browser.find_element(
            By.CLASS_NAME, 'yidun_jigsaw').get_attribute('src')
        req = requests.get(bg_url)
        with open('slide_bg.png', 'wb') as f:
            f.write(req.content)
        bg_png = cv2.imread('slide_bg.png', 0)

        req = requests.get(tg_url)
        with open('slide_tg.png', 'wb') as f:
            f.write(req.content)
        tg_png = cv2.imread('slide_tg.png', 0)
        req.close()
        return bg_png, tg_png


login = Login()



