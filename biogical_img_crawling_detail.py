from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openpyxl
import time
import os

def save_last_ktsn(ktsn):
    with open('last_ktsn.txt', 'w') as f:
        f.write(str(ktsn))

def load_last_ktsn():
    if os.path.exists('last_ktsn.txt'):
        with open('last_ktsn.txt', 'r') as f:
            return int(f.read().strip())
    return None

def main():
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['대분류', '중분류', '이미지 URL'])

    wb1 = openpyxl.load_workbook('list_ktsn.xlsx')
    ws1 = wb1.active

    # 마지막으로 처리한 ktsn 번호 불러오기
    last_ktsn = load_last_ktsn()

    start_reading = False if last_ktsn else True

    driver = webdriver.Chrome(executable_path='C:\chromedriver.exe')

    mammal_arr = []
    for cell in ws1["A"]:
        if cell.value:
            if not start_reading and cell.value == last_ktsn:
                start_reading = True
                continue
            if start_reading:
                mammal_arr.append(cell.value)

    for ktsn in mammal_arr:
        driver_url = f"https://species.nibr.go.kr/home/mainHome.do?cont_link=009&subMenu=009002&contCd=009002&pageMode=view&ktsn={ktsn}"
        driver.get(driver_url)
        
        
        time.sleep(1)
        print("driver_url: ", driver_url)
        try:
            div_tag = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "swiper-zoom-container"))
            )
            img_url = div_tag.find_element(By.TAG_NAME, "img").get_attribute("src")
            ktsn_name = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "txtW"))
            ).find_element(By.TAG_NAME, "h3").text
            print("img_url: ", img_url, ktsn_name)
            ws.append(['대분류', ktsn_name, img_url])
            wb.save("mammal_img_url.xlsx")
            save_last_ktsn(ktsn)
            time.sleep(1)

        except Exception as e:
            print(f"Error processing {ktsn}: {e}")

    driver.quit()

if __name__ == '__main__':
    main()
