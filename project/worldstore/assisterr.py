import time
import uuid

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import recognition as AICloud
from pynput.keyboard import Key, Controller as KeyboardController
import json
import util
import config

driver = None


def open_driver():
    # 创建一个Chrome浏览器实例
    chrome_options = Options()
    chrome_options.page_load_strategy = 'eager'
    # chrome_options.add_argument("--incognito")  # 设置为隐私模式

    chrome_options.add_extension(config.plugin_path)

    # 指定ChromeDriver的路径
    s = Service(executable_path=config.executable_path)

    # 创建一个Chrome浏览器实例，并指定ChromeDriver的路径
    return webdriver.Chrome(service=s, options=chrome_options)


def disconnect_wallet():
    switch_handle("assisterr")
    driver.find_elements(By.XPATH, '//span[contains(text(),"...")]')[0].click()
    util.click(driver, By.XPATH, '//span[text()="Disconnect"]')
    time.sleep(2)


def switch_handle(keywords_str):
    keywords = keywords_str.split(",")
    window_index = 0
    loop_times = 0
    while loop_times < 10:  # 等待10s，避免窗口没来得及打开
        time.sleep(1)
        if window_index >= len(driver.window_handles):
            # 所有页面都找完后没有插件页面
            window_index = 0

            # 打开插件页面，循环打开，避免插件页面打不开的问题
            while True:
                keyboard_c = KeyboardController()
                with keyboard_c.pressed(Key.shift, Key.alt):
                    keyboard_c.press("o")
                time.sleep(2)
                driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
                if "chrome" not in driver.current_url:
                    time.sleep(1)
                    continue
                return
        driver.switch_to.window(driver.window_handles[window_index])
        for keyword in keywords:
            if keyword in driver.current_url:
                print("找到页面了，url = " + driver.current_url)
                return
        window_index = window_index + 1


class Assisterr:
    def __init__(self):
        self.account_num = 500  # 单个钱包的账户数量
        self.wallet_data_json = {}
        self.current_wallet_id = None
        self.twitter_token = None
        self.twitter_tokens = []
        self.discord_token = None
        self.discord_tokens = []
        self.account_index = 1
        self.follow_url = ""

    def twitter_login(self):
        switch_handle("okx,crypto,x.com")
        driver.get("https://x.com/")
        # token 已经用完
        if len(self.twitter_tokens) == 0:
            print("没有token了")
        self.twitter_token = self.twitter_tokens[0]
        cookies = {'value': self.twitter_token, 'name': 'auth_token'}
        driver.add_cookie(cookie_dict=cookies)

        driver.get("https://x.com/home")
        time.sleep(3)

    def discord_login(self):
        switch_handle("okx,crypto,x.com")
        driver.get('https://discord.com/login')  # 打开Discord
        # 登录页面
        js = """
        function login(token) {
        setInterval(() => {
        document.body.appendChild(document.createElement('iframe')).content
        Window.localStorage.token = `"${token}"`
        }, 50);
        setTimeout(() => {
        location.reload();
        }, 500);
        }
        """
        time.sleep(3)  # 等待页面加载
        self.discord_token = self.discord_tokens[0]
        driver.execute_script(js + f'login("{self.discord_token}")')

    def switch_wallet(self):
        if self.account_index >= self.account_num:
            return
        switch_handle("chrome")
        account_element = driver.find_element(By.XPATH, '//div[contains(text(),"账户")]')
        account_index = account_element.text.replace("账户 ", "")
        account_element.click()

        time.sleep(1)

        for _ in range(self.account_index - int(account_index) + 1):
            try:
                while True:
                    targets = driver.find_elements(By.CLASS_NAME, "okx-wallet-plugin-plus")
                    if len(targets) == 0:
                        time.sleep(1)
                        continue
                    last_target = targets[len(targets) - 1]
                    driver.execute_script("arguments[0].scrollIntoView();", last_target)
                    last_target.click()
                    break
            except Exception as e1:
                print(e1)
            time.sleep(1)

        self.account_index = self.account_index + 1
        next_account_name = str(self.account_index)
        if self.account_index < 10:
            next_account_name = "0" + next_account_name
        next_account_name = "账户 " + next_account_name
        account_elements = driver.find_elements(By.XPATH, '//div[text()="' + next_account_name + '"]')
        account_elements[len(account_elements) - 1].click()

    def wallet_login(self):
        # 打开一个网址
        driver.get("https://build.assisterr.ai/?ref=666a657c99966fe1fc5e2e68")
        time.sleep(1)
        switch_handle("chrome")

        if self.current_wallet_id is not None:
            util.click(driver, By.XPATH, '//span[text()="导入已有钱包"]')
            util.click(driver, By.XPATH, '//div[text()="助记词或私钥"]')
            time.sleep(2)
            current_wallet_data = self.wallet_data_json[self.current_wallet_id]
            word_list = current_wallet_data["word_list"]
            for i, password_input in enumerate(driver.find_elements(By.TAG_NAME, "input")):
                password_input.send_keys(word_list[i])
            time.sleep(3)
            util.click(driver, By.XPATH, '//span[text()="确认"]')
            time.sleep(3)

            while True:
                password_input_elements = driver.find_elements(By.TAG_NAME, "input")
                if len(password_input_elements) == 0:
                    time.sleep(1)
                    continue
                for password_input in driver.find_elements(By.TAG_NAME, "input"):
                    password_input.send_keys("12345678")
                break
            util.click(driver, By.XPATH, '//span[text()="确认"]')
            util.click(driver, By.XPATH, '//span[text()="设为默认钱包"]')
            util.click(driver, By.XPATH, '//span[text()="开启你的 Web3 之旅"]')
            self.switch_wallet()
            driver.close()
        else:
            util.click(driver, By.XPATH, '//span[text()="创建新钱包"]')
            util.click(driver, By.XPATH, '//div[text()="助记词"]')
            time.sleep(3)
            while True:
                password_input_elements = driver.find_elements(By.TAG_NAME, "input")
                if len(password_input_elements) == 0:
                    time.sleep(1)
                    continue
                for password_input in driver.find_elements(By.TAG_NAME, "input"):
                    password_input.send_keys("12345678")
                break

            util.click(driver, By.XPATH, '//span[text()="确认"]')
            util.click(driver, By.XPATH, '//span[text()="设为默认钱包"]')
            util.click(driver, By.XPATH, '//span[text()="开启你的 Web3 之旅"]')
            self.backup_wallet()

    def backup_wallet(self):
        util.click(driver, By.XPATH, '//span[text()="立即备份"]')

        driver.find_element(By.TAG_NAME, "input").send_keys("12345678")
        util.click(driver, By.XPATH, '//span[text()="确认"]')

        util.click(driver, By.CLASS_NAME, "okx-wallet-plugin-eye")
        time.sleep(1)
        word_dict = {}
        wallet_data = {
            "word_list": [],
            "word_index": [],
            "twitter_follow": [],
            "discord_follow": [],
            "account_index": 1,
            "id": str(uuid.uuid4())

        }
        for i in range(12):
            canvas_js = 'return document.getElementsByTagName("canvas")[' + str(i) + '].toDataURL("image/png");'
            # 执行 JS 代码并拿到图片 base64 数据
            im_info = driver.execute_script(canvas_js)  # 执行js文件得到带图片信息的图片数据
            im_base64 = im_info.split(',')[1]
            word = AICloud.request(str(i), im_base64)
            word_dict[str(i + 1)] = word
            wallet_data["word_list"].append(word)
        util.click(driver, By.XPATH, '//span[text()="我已记录完毕"]')
        time.sleep(1)
        for word_element in driver.find_elements(By.XPATH, '//div[contains(text(),"#")]'):
            index = word_element.text.replace("#", "")
            wallet_data["word_index"].append(index)
            util.click(driver, By.XPATH, '//div[text()="' + word_dict[index] + '"]')
        self.wallet_data_json[wallet_data["id"]] = wallet_data
        self.current_wallet_id = wallet_data["id"]
        self.write_json()

    def connect_wallet(self, account_index):
        print("正在连接第" + str(account_index) + "个钱包账号")
        switch_handle("assisterr")

        # 通过按钮名称找到按钮元素
        util.click(driver, By.XPATH, '//button[text()="Select Wallet"]')

        util.click(driver, By.XPATH, '//span[text()="Detected"]')

        time.sleep(3)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
        if "chrome" not in driver.current_url:
            switch_handle("chrome")
        util.click(driver, By.XPATH, '//div[text()="连接"]')

        time.sleep(3)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
        # 避免悬浮窗口未弹出
        if "chrome" not in driver.current_url:
            switch_handle("chrome")
        util.click(driver, By.XPATH, '//div[text()="确认"]')

        time.sleep(1)
        driver.switch_to.window(driver.window_handles[len(driver.window_handles) - 1])
        # 避免悬浮窗口未弹出
        if "chrome" not in driver.current_url:
            switch_handle("chrome")
        util.click(driver, By.XPATH, '//div[text()="确认"]')

        switch_handle("assisterr")
        time.sleep(3)

        try:
            driver.find_element(By.XPATH, '//button[text()="X (Twitter) auth"]')
        except Exception as e:
            print(e)
            # 没找到，第一次链接
            util.click(driver, By.XPATH, '//button[text()="Start building"]')

        self.twitter_follow()
        # self.discord_follow()

        self.wallet_data_json.get(self.current_wallet_id)["account_index"] = self.account_index
        self.write_json()

        disconnect_wallet()

    def twitter_follow(self):
        followed_success = False
        while not followed_success:

            ws.twitter_login()
            switch_handle("assisterr")
            # twitter关注
            util.click(driver, By.XPATH, '//button[text()="X (Twitter) auth"]')
            time.sleep(10)
            print(driver.current_url)
            driver.get(driver.current_url.replace("twitter.com", "x.com"))

            util.click(driver, By.XPATH, '//span[text()="Authorize app"]')

            for _ in range(5):
                if "assisterr" in driver.current_url:
                    time.sleep(10)
                    if "already" not in driver.current_url:
                        followed_success = True
                    break
                time.sleep(2)
            self.wallet_data_json.get(self.current_wallet_id)["twitter_follow"].append(self.twitter_token)
            # 只剩一个token时，不删除
            if len(self.twitter_tokens) > 1:
                self.twitter_tokens.remove(self.twitter_token)
                self.write_tokens("twitter")

    def discord_follow(self):
        self.discord_login()
        switch_handle("assisterr")
        # twitter关注
        util.click(driver, By.XPATH, '//button[text()="Discord auth"]')
        time.sleep(5)
        util.click(driver, By.XPATH, '//div[text()="授权')
        time.sleep(5)
        self.wallet_data_json.get(self.current_wallet_id)["discord_follow"].append(self.discord_token)
        if len(self.discord_tokens) > 1:
            self.discord_tokens.remove(self.discord_token)
            self.write_tokens("discord")

    def write_json(self):
        with open(config.wallet_path, "w") as f:
            print(self.wallet_data_json)
            json.dump(self.wallet_data_json, f)

    def write_tokens(self, token_type):
        if token_type == "twitter":
            with open(config.twitter_tokens_path, "w") as f:
                for t in self.twitter_tokens:
                    f.write(t + "\n")
        else:
            with open(config.discord_tokens_path, "w") as f:
                for t in self.discord_tokens:
                    f.write(t + "\n")


if __name__ == '__main__':
    ws = Assisterr()
    with open(config.twitter_tokens_path, 'r') as token_f:
        for token in token_f.readlines():
            ws.twitter_tokens.append(token.strip().replace('\n', ''))
    with open(config.discord_tokens_path, 'r') as token_f:
        for token in token_f.readlines():
            ws.discord_tokens.append(token.strip().replace('\n', ''))
    with open(config.wallet_path, "r") as wallet_f:
        wallet_json = json.loads(wallet_f.read())
        ws.wallet_data_json = wallet_json
        for k, v in wallet_json.items():
            if v["account_index"] < 500:
                ws.current_wallet_id = k

    try:
        while True:
            driver = open_driver()

            if ws.current_wallet_id is not None:
                wd = wallet_json[ws.current_wallet_id]
                if "account_index" in wd:
                    ws.account_index = wd["account_index"]
                else:
                    ws.account_index = 1
                if ws.account_index == ws.account_num:
                    ws.current_wallet_id = None
                    ws.account_index = 1
            ws.wallet_login()
            # ws.discord_login()
            for i in range(ws.account_index, ws.account_num + 1):
                ws.connect_wallet(i)
                ws.switch_wallet()
            # 清空当前钱包，重新创建新的钱包
            ws.current_wallet_id = None
            ws.account_index = 1
            driver.quit()

    except Exception as e:
        print(e)
    # finally:
    # driver.quit()
    # driver.close()
