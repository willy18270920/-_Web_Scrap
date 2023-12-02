'''
此為使用Selenium自動化爬取官網"網紅配方"的爬蟲程式碼
需先執行"KOL_Index_csv_main.ipynb"將全部網紅的內頁連結爬下來
此程式碼可以爬到網紅ID、網紅名字、追蹤數、平均互動貼文數、IG網址、FB網址、產業分類、外型/形象、合作品項、子頁網址
'''
'''
This code is an automated web scraping script using Selenium for the "網紅配方" official website.
To use it, you need to first execute "KOL_Index_csv_main.ipynb" to crawl all the individual page links for influencers. 
This script can extract information such as influencer ID, name, follower count, average interactive posts, Instagram URL, Facebook URL, industry category, appearance/image, collaboration items, and subpage URL.
'''
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from time import sleep
import re
import os
import csv
import random
username = '123@gmail.com'  # type loggin username
pwd = '123'  # type loggin passwd

# 檢查保存數據的目錄是否存在，不存在則創建
save_dir = './KOL_info'
if not os.path.exists(save_dir):
    print(f"保存數據的目錄 {save_dir} 不存在，已創建 {save_dir}")
    os.makedirs(save_dir)
else:
    print("KOL_info 目錄已存在，將開始爬蟲")

# 配置Chrome WebDriver
my_options = webdriver.ChromeOptions()
my_options.add_argument("--start-maximized")
my_options.add_argument("--incognito")
my_options.add_argument("--disable-popup-blocking")
my_options.add_argument("--disable-notifications")
my_options.add_argument("--lang=zh-TW")

# 初始化Chrome WebDriver
driver = webdriver.Chrome(options=my_options)

# 定義存儲數據的列表
kol_idf = []
kol_namef = []
follower_countf = []
average_interactionf = []
instagram_urlf = []
facebook_urlf = []
industriesf = []
appearf = []
cooperatef = []
kol_id_contentf = []

# 訪問網站


def visit():
    url = "https://www.prefluencer.com/brands/login"
    driver.get(url)
    sleep(1)

# 登錄


def login():
    account = driver.find_element(By.CSS_SELECTOR, "input#login_account")
    account.send_keys(username)
    sleep(1)
    password = driver.find_element(By.CSS_SELECTOR, "input#login_password")
    password.send_keys(pwd)
    sleep(1)
    button = driver.find_element(
        By.CSS_SELECTOR, "button.btn.btn--block.btn--primary.btn--square.btn-login")
    button.click()
    sleep(3)

# 爬取數據


def crawl():
    # 讀取URL列表
    file_path = "./KOL內頁網址10K-50K.csv"
    urls = []

    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳過標題行
            for row in reader:
                url = row[1]
                urls.append(url)
    except Exception as e:
        print(f"讀取URL文件時發生錯誤: {e}")

    # 打開CSV文件以追加模式
    csv_file_path = os.path.join(save_dir, f"KOL詳細資料_10K-50K.csv")
    with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ['KOL ID', 'KOL名字', '追蹤數', '平均貼文互動數',
                      'Instagram 網址', 'Facebook 網址', '產業分類', '外型/形象', '合作品項', '子頁網址']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for url in urls:
            try:
                # 發送GET請求並獲取網頁內容
                driver.get(url)

                # 解析網頁內容
                soup = bs(driver.page_source, "lxml")
                kol_id = soup.select('meta[property="og:url"]')
                kol_name_elements = soup.select('span.kol-info__name-content')
                follower_elements = soup.select(
                    'li.statistics__item p.statistics__text')
                interaction_elements = soup.select(
                    'li.statistics__item.statistics__item--large p.statistics__text')
                instagram_url_elements = soup.select(
                    'p.kol-info__info-content a[title="instagram" i]')
                facebook_url_elements = soup.select(
                    'p.kol-info__info-content a[title="facebook" i]')
                industry_element = soup.select_one(
                    'div.kol-info__info-field:has(h4.kol-info__info-title:-soup-contains("產業分類")) p.kol-info__info-content')
                appearance_element = soup.select_one(
                    'div.kol-info__info-field:has(h4.kol-info__info-title:-soup-contains("外型/形象")) p.kol-info__info-content')
                coop_element = soup.select_one(
                    'div.kol-info__info-field:has(h4.kol-info__info-title:-soup-contains("合作品項")) p.kol-info__info-content')

                # 獲取KOL ID
                if kol_id:
                    kol_id_content = kol_id[0].get("content")
                    kol_ids = re.search(r'\d+', kol_id_content)
                    if kol_ids:
                        kol_id_number = kol_ids.group()
                        kol_idf.append(kol_id_number)

                # 獲取KOL名字
                if kol_name_elements:
                    kol_names = [
                        kol_name_element.text for kol_name_element in kol_name_elements]
                    kol_namef.append(', '.join(kol_names))

                # 獲取追蹤數，只抓第三項
                if len(follower_elements) > 2:
                    third_follower = follower_elements[2].text
                    try:
                        if 'k' in third_follower:
                            third_follower = third_follower.replace('k', '')
                            follower_count_int = int(
                                float(third_follower) * 1000)
                        elif 'M' in third_follower:
                            third_follower = third_follower.replace('M', '')
                            follower_count_int = int(
                                float(third_follower) * 1000000)
                        else:
                            follower_count_int = int(
                                third_follower.replace(',', ''))
                        follower_countf.append(follower_count_int)
                    except ValueError:
                        print(f"無法將'{third_follower}'轉換為整數。")

                # 獲取平均互動
                average_interactions = [
                    interaction_element.text for interaction_element in interaction_elements]
                try:
                    if 'k' in average_interactions[0]:
                        average_interactions[0] = average_interactions[0].replace(
                            'k', '')
                        average_interaction_int = int(
                            float(average_interactions[0]) * 1000)
                    elif 'M' in average_interactions[0]:
                        average_interactions[0] = average_interactions[0].replace(
                            'M', '')
                        average_interaction_int = int(
                            float(average_interactions[0]) * 1000000)
                    else:
                        average_interaction_int = int(
                            average_interactions[0].replace(',', ''))
                    average_interactionf.append(average_interaction_int)
                except ValueError:
                    print(f"無法將'{average_interactions[0]}'轉換為整數.")

                # 獲取IG網址連結
                if instagram_url_elements:
                    instagram_urls = [element['href']
                                      for element in instagram_url_elements]
                    instagram_urlf.append(', '.join(instagram_urls))

                # 獲取FB網址連結
                if facebook_url_elements:
                    facebook_urls = [element['href']
                                     for element in facebook_url_elements]
                    facebook_urlf.append(', '.join(facebook_urls))
                else:
                    facebook_urlf.append("None")

                # 獲取產業分類
                if industry_element:
                    industry_text = industry_element.get_text(strip=True)
                    industry_text = industry_text.replace('\n', '')
                    industries = [item.strip()
                                  for item in industry_text.split(',')]
                    industriesf.append(', '.join(industries))
                else:
                    industriesf.append("None")

                # 獲取外型/形象
                if appearance_element:
                    appearance_text = appearance_element.get_text(strip=True)
                    appearance_text = appearance_text.replace('\n', '')
                    appear = [item.strip()
                              for item in appearance_text.split(',')]
                    appearf.append(', '.join(appear))
                else:
                    appearf.append("None")

                # 獲取合作品項
                if coop_element:
                    coop_text = coop_element.get_text(strip=True)
                    coop_text = coop_text.replace('\n', '')
                    cooperate = [item.strip() for item in coop_text.split(',')]
                    cooperatef.append(', '.join(cooperate))
                else:
                    cooperatef.append("None")

                # 獲取子頁網址
                if kol_id:
                    kol_id_content = kol_id[0].get("content")
                    kol_id_contentf.append(kol_id_content)

                # 寫入CSV文件
                writer.writerow({'KOL ID': kol_idf[-1], 'KOL名字': kol_namef[-1], '追蹤數': follower_countf[-1], '平均貼文互動數': average_interactionf[-1], 'Instagram 網址': instagram_urlf[-1],
                                'Facebook 網址': facebook_urlf[-1], '產業分類': industriesf[-1], '外型/形象': appearf[-1], '合作品項': cooperatef[-1], '子頁網址': kol_id_contentf[-1]})

                # 生成介於30到90秒之間的隨機數
                delay = random.randint(30, 90)
                # 休眠指定的秒數
                sleep(delay)

                print(f"已完成 {len(kol_idf)} 條記錄")

            except Exception as e:
                # 發生異常時記錄錯誤信息，並等待10分鐘
                print(f"爬取網址時發生錯誤: {e}，休息10分鐘")
                with open("./KOL_info/error_log_10K-50K.csv", "a", newline='', encoding='utf-8-sig') as error_log_file:
                    error_log_writer = csv.writer(error_log_file)
                    error_log_writer.writerow([url, str(e)])
                    sleep(600)
                continue  # 繼續處理下一個URL

    print("爬蟲已完成")
    print(f"CSV文件儲存成功，腳本已結束")


if __name__ == "__main__":
    visit()
    login()
    crawl()
