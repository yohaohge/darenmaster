import os.path
import json
import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

conf = {}
# 启动程序， 打开登录页面
driver_manager = {}


def get_driver():
    print("获取driver")
    global driver_manager
    if "driver" in driver_manager:
        return driver_manager["driver"]
    else:
        conf = {}
        if os.path.exists("ini/conf.json"):
            with open("ini/conf.json", "r", encoding="utf-8") as file:
                content = file.read()
                conf = json.loads(content)

        if "driver" in conf and conf["driver"] == "edge":
            option = webdriver.EdgeOptions()
            if "user-data-dir" in conf and conf["user-data-dir"] != "":
                option.add_argument("--user-data-dir=" + conf["user-data-dir"])
            driver = webdriver.Edge(options=option)
        else:
            option = webdriver.ChromeOptions()
            if "user-data-dir" in conf and conf["user-data-dir"] != "":
                option.add_argument("--user-data-dir=" + conf["user-data-dir"])
            driver = webdriver.Chrome(options=option)

        driver_manager["driver"] = driver
        # 进入登录窗口
        driver.get("https://seller.tiktokglobalshop.com/account/login")

        return driver_manager["driver"]


def reload_driver():
    if "driver" in driver_manager:
        driver_manager["driver"].quit()
        driver_manager.clear()
    get_driver()


if __name__ == "__main__":
    driver = get_driver()
    print(driver.current_url)
    time.sleep(20)
