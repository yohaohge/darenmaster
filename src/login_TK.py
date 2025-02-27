from __init__ import *
import time
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from util import *
import re

def get_home_info()->str:

    driver = get_driver()
    switch_to_target("https://affiliate.tiktokglobalshop.com/platform/homepage")
    for _ in range(5):
        try:
            element = driver.find_element(by=By.XPATH,
                                            value="/html/body/div[1]/div/div[1]/div[2]/div/div[4]/div")

            driver.execute_script("arguments[0].click();", element)
            time.sleep(1)
            html_content = driver.page_source
            all = re.findall('<div class="text-body-m-medium text-neutral-text1">(.*)</div></div></div><div class="text-body-s text-neutral-text4">Shop Code', html_content)
            print(all)
            return all[0]
        except:
            time.sleep(1)

    return ""
def loginTK() -> bool:
    driver = get_driver()
    url = "https://seller.tiktokglobalshop.com/account/login?redirect_url=https%3A%2F%2Faffiliate.tiktokglobalshop.com"
    # 打开网页
    driver.get(url)
    time.sleep(2)

    if "login" in driver.current_url:
        element = driver.find_element(by=By.XPATH,
                                      value="/html/body/div/section/section/div/div/div/div[1]/section/div[1]/div[4]/div[2]/span[2]")
        driver.execute_script("arguments[0].click();", element)
        time.sleep(1)
        username_field = driver.find_element(by=By.ID, value="TikTok_Ads_SSO_Login_Email_Input")  # 使用实际网页上的用户名输入框的ID
        username_field.send_keys("13277092207@163.com")

        time.sleep(1)
        password_field = driver.find_element(by=By.ID, value="TikTok_Ads_SSO_Login_Pwd_Input")  # 使用实际网页上的用户名输入框的ID
        password_field.send_keys("zhangou123@@")
        password_field.send_keys(Keys.RETURN)

        time.sleep(1)
        login_btn = driver.find_element(by=By.ID,
                                       value="TikTok_Ads_SSO_Login_Btn")
        driver.execute_script("arguments[0].click();", login_btn)

        while "login" in driver.current_url:
            print("登录中")
            time.sleep(10)
        return True
    else:
        print("不是登录页面")
        return True
