from selenium import webdriver
import openpyxl
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
from selenium.common.exceptions import NoAlertPresentException, TimeoutException, NoSuchElementException

from database_connect import db_connect

def main():
    wb = openpyxl.Workbook()
    # ws = wb.active
    # ws.append(['대분류', '중분류', '이미지 URL'])

    wb1 = openpyxl.load_workbook('list_ktsn.xlsx')
    ws1 = wb1.active

    try:
        chrome_driver_path = 'C:\\chromedriver.exe'
        service = Service(executable_path=chrome_driver_path)
        driver = webdriver.Chrome(service=service)
        
        cursor, conn = db_connect()
        for cell in ws1["A"]:
            time.sleep(2)
            driver_url = f"https://species.nibr.go.kr/home/mainHome.do?cont_link=009&subMenu=009002&contCd=009002&pageMode=view&ktsn={cell.value}"
            print("driver_url:", driver_url)
            driver.get(driver_url)

            try:
                # Alert 확인
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"Skipping {cell.value} due to alert: {alert_text}")
                alert.accept()
                continue
            except TimeoutException:
                print("No alert present, continuing...")

            try:
                # tit 클래스의 텍스트를 대기하고 가져옴
                ko_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'tit'))
                ).text
                print("Title Text:", ko_name)

                # .stxt 클래스의 텍스트를 대기하고 가져옴
                en_name = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'stxt'))
                ).text
                print("Scientific Name:", en_name)

                # class-system 내의 텍스트를 대기하고 가져옴
                class_system_texts = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.class-system .txt a'))
                )
                class_system_text_list = [element.text for element in class_system_texts]

                print("Classification System Texts:")
                step_arr =[]
                for text in class_system_text_list:
                    print(f" {text}")
                    step_arr.append(text)

                phylum_nm = step_arr[1] if len(step_arr) > 1 else '' # 문
                class_nm = step_arr[2] if len(step_arr) > 2 else '' # 강
                order_nm = step_arr[3] if len(step_arr) > 3 else '' # 목
                family_nm = step_arr[4] if len(step_arr) > 4 else '' # 과
                genus_nm = step_arr[5] if len(step_arr) > 5 else '' # 속
                # img src 속성을 대기하고 가져옴 
                try:
                    img_src = WebDriverWait(driver, 10).until( EC.presence_of_element_located
                                        ((By.CSS_SELECTOR, '.visual-bg01 .swiper-zoom-container img'))).get_attribute('src')
                except TimeoutException:
                    img_src = ""
                
                insert_sql = f'''
                    INSERT INTO tb_gt_biological_species (korNm, enNm, phylumNm, classnm, ordernm, familynm, genusnm, imageUrl)
                    VALUES ("{ko_name}", "{en_name}", "{phylum_nm}", "{class_nm}", "{order_nm}", "{family_nm}", "{genus_nm}", "{img_src}")
                    ON DUPLICATE KEY UPDATE
                        enNm = VALUES(enNm),
                        phylumNm = VALUES(phylumNm),
                        classnm = VALUES(classnm),
                        ordernm = VALUES(ordernm),
                        familynm = VALUES(familynm),
                        genusnm = VALUES(genusnm),
                        imageUrl = VALUES(imageUrl);
                    '''
                print(" insert_sql : \n\n\n", insert_sql)
            # time.sleep(1) 
                cursor.execute(insert_sql)

            except (TimeoutException, NoSuchElementException) as e:
                print(f"Error processing {cell.value}: {str(e)}")

            conn.commit() 
            print("\n==============================================")
            time.sleep(1)

    except Exception as e:
        print(f"Error processing: {str(e)}")

    finally:
        driver.quit()
        conn.close()

if __name__ == '__main__':
    main()
