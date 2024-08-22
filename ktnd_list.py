from selenium import webdriver
from selenium.webdriver.common.by import By
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
    mammal_arr = []
        
    wb = openpyxl.Workbook()
    ws = wb.active  # 현재 활성화된 셀을 보는 것
    ws.append(['대분류', 'ktsn' ,'생물 명', '이미지 URL'])
    wb1 = openpyxl.load_workbook('list_ktsn.xlsx')
    ws1 = wb1.active
    col = ws1["A"]  # 영어 column 만 가지고 오기
    # col_B 값 출력하기
    for cell in col:
        mammal_arr.append(cell.value)

    # 마지막으로 처리한 ktsn 번호 불러오기
    last_ktsn = load_last_ktsn()
    print("\n\n")
    if last_ktsn is not None:
        start_index = mammal_arr.index(str(last_ktsn)) +1 
    else:
        start_index = 0

    driver = webdriver.Chrome()
    driver_url = ""
    



    for ktsn in mammal_arr[start_index:]:
        driver_url = f"https://species.nibr.go.kr/home/mainHome.do?cont_link=009&subMenu=009002&contCd=009002&pageMode=view&ktsn={ktsn}"
        driver.get(driver_url)
        print("driver_url: ", driver_url)
        try:
            div_tag = driver.find_element(By.CLASS_NAME, "swiper-zoom-container")
            time.sleep(1)
            img_url = div_tag.find_element(By.TAG_NAME, "img").get_attribute("src")
            ktsn_name = driver.find_element(By.CLASS_NAME, "txtW").find_element(By.TAG_NAME, "h3").text
            print("img_url: ", img_url, ktsn_name, "\n")
            ws.append(['대분류', ktsn, ktsn_name, img_url])
            wb.save("mammal_img_url.xlsx")
            save_last_ktsn(ktsn)  # 마지막으로 처리한 ktsn 번호 저장

        except Exception as e:
            print(f"Error processing {ktsn}")

    driver.quit()

if __name__ == '__main__':
    
    main()
