import sys

from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QDateTime, pyqtSignal
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests


class DriverRun(QtCore.QThread):
    _signal = pyqtSignal(str)
    startime = ''

    def __init__(self):
        super(DriverRun, self).__init__()

    def run(self):
        address = 'https://www.taobao.com/'
        print("###抢购时间=" + self.startime + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # 打开无头浏览器
        chrome_opt = Options()  # 创建参数设置对象.
        chrome_opt.add_argument('--disable-infobars')  # 隐藏"Chrome正在受到自动软件的控制"
        chrome_opt.add_argument('--window-size=1366,768')
        chrome_opt.add_argument('--headless')  # 无界面化.
        chrome_opt.add_argument('--disable-gpu')  # 配合上面的无界面化.
        chrome_opt.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        driver = webdriver.Chrome(chrome_options=chrome_opt)  # 创建Chrome对象.
        driver.maximize_window()
        driver.get(address)
        # 点击登录
        login_button = WebDriverWait(driver, 5, 0.1).until(
            expected_conditions.presence_of_element_located((By.LINK_TEXT, "亲，请登录")), "亲，请登录 按钮未找到")
        print("###亲，请登录 按钮已定位" + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        login_button.click()
        while True:
            try:
                j_qr_code_img = WebDriverWait(driver, 5, 0.1).until(
                    expected_conditions.presence_of_element_located((By.XPATH, '//*[@id="J_QRCodeImg"]/img')),
                    "二维码图片未找到")
                url = j_qr_code_img.get_attribute('src')
                print('###二维码图片 已定位' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                r = requests.get(url)
                with open('./J_QRCodeImg.png', 'wb') as f:
                    f.write(r.content)
                self._signal.emit('替换二维码')
                cart_button = WebDriverWait(driver, 60, 3).until(
                    expected_conditions.presence_of_element_located((By.XPATH, '//span[contains(text(),"购物车")]')),
                    "购物车 按钮未找到")
                cart_button.click()
                self._signal.emit('初始化图片')
                print('###购物车 按钮已定位' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                # 保存cookie 关闭浏览器
                cookies = driver.get_cookies()
                f = open("loginCookie.txt", 'w+')
                f.write(str(cookies))
                f.flush()

                break
            except Exception as e:
                print(e)
                driver.refresh()
        # 点击全选
        select_all_button = WebDriverWait(driver, 5, 0.1).until(
            expected_conditions.presence_of_element_located((By.ID, 'J_SelectAll1')), "点击全选 按钮未找到")
        print('###全选按钮 已定位' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        select_all_button.click()
        while True:
            try:
                cart_num = WebDriverWait(driver, 5, 0.1).until(
                    expected_conditions.presence_of_element_located((By.ID, 'J_SelectedItemsCount')), "购物车数量 按钮未找到")
                count = cart_num.text
                if count != '0':
                    print('###锁定购物车,数量:' + count + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    break
            except Exception as e:
                print(e)
                driver.refresh()

        # 点击结算
        submit_button = WebDriverWait(driver, 5, 0.1).until(
            expected_conditions.presence_of_element_located((By.ID, 'J_Go')), "结算 按钮未找到")
        print('###结算按钮 已定位' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        while True:
            try:
                local_time_stamp = int(time.time())
                # 抢购时间
                start_time_stamp = int(time.mktime(time.strptime(self.startime, "%Y-%m-%d %H:%M:%S")))

                if start_time_stamp - local_time_stamp > 100:
                    time.sleep(60)
                    print("###时间尚早，睡眠1分钟!" + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                if local_time_stamp >= start_time_stamp:
                    print("###时间已到...开抢" + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    break
            except Exception as e:
                print(e)
        print('###点击结算按钮' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        submit_button.click()
        # 提交订单
        loop_count = 0
        while loop_count < 10:
            try:
                loop_count = loop_count + 1
                print("###循环次数=" + str(loop_count) + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                create_order_button = WebDriverWait(driver, 5, 0.1).until(
                    expected_conditions.presence_of_element_located((By.CLASS_NAME, 'go-btn')), "提交订单 按钮未找到")
                print('###提交订单按钮 已定位' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                create_order_button.click()
                break
            except Exception as e:
                driver.save_screenshot(
                    './screenshot/error' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '.png')
                print(e)
                driver.refresh()
        driver.save_screenshot('./screenshot/finish' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + '.png')
        print('###脚本执行完毕...检查订单' + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        driver.close()


class taobaoBot(QWidget):
    def __init__(self):
        super(taobaoBot, self).__init__()
        self.initUI()

    def initUI(self):
        # 设置窗口的标题与初始大小
        self.setWindowTitle('Fast Go !!!')
        self.resize(200, 200)
        # 垂直布局
        vlayout = QVBoxLayout()
        # 实例化编辑时间日期的控件
        # 默认下，不指定日期的时间，系统会设置一个和本地相同的日期时间格式，时间默认2000年1月1日0时0分0秒
        # 指定当前日期时间为控件的日期时间
        dateTimeEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        # 设置日期时间格式，可以选择/ . : -等符号自定义数据连接符
        dateTimeEdit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        # 添加确定按钮
        button = QPushButton("开始抢购", self)
        button.clicked.connect(lambda: self.on_click(dateTimeEdit))
        pixmap = QPixmap("./initImage.png")
        lbl = QLabel(self)
        lbl.setPixmap(pixmap)
        vlayout.addWidget(lbl)
        # 布局控件添加，设置主窗口的布局
        vlayout.addWidget(dateTimeEdit)
        vlayout.addWidget(button)
        self.setLayout(vlayout)

    def call_back_ui_reload(self, msg):
        if msg == '替换二维码':
            pixmap = QPixmap("./J_QRCodeImg.png")
            self.findChild(QLabel).setPixmap(pixmap)
        else:
            pixmap = QPixmap("./initImage.png")
            self.findChild(QLabel).setPixmap(pixmap)
        QApplication.processEvents()

    def on_click(self, startime):
        print("###程序已启动" + '->' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        # 创建线程
        self.thread = DriverRun()
        # 添加参数
        self.thread.startime = startime.text()
        # 连接信号
        self.thread._signal.connect(self.call_back_ui_reload)
        # 开始线程
        self.thread.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    taobaoBot = taobaoBot()
    taobaoBot.show()
    sys.exit(app.exec_())
