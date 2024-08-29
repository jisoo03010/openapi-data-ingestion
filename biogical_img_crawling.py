from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
from selenium.common.exceptions import NoAlertPresentException

import re
from database_connect import db_connect
def main():
    driver = webdriver.Chrome(executable_path='C:\chromedriver.exe')

    driver_url = "https://species.nibr.go.kr/home/mainHome.do?cont_link=002&subMenu=002003&contCd=002003002"
    driver.get(driver_url)
    cursor, conn = db_connect()
    
    # chrome_driver_path = 'C:\\chromedriver.exe'
    # # Set Chrome options
    # options = webdriver.ChromeOptions()
    # options.add_argument("headless")
    # service = Service(executable_path=chrome_driver_path)
    # driver = webdriver.Chrome(service=service, options=options)
    # driver_url = "https://species.nibr.go.kr/home/mainHome.do?cont_link=002&subMenu=002003&contCd=002003002"
    # driver.get(driver_url)
    try:
        
        wait = WebDriverWait(driver, 10)  # Explicit Wait 설정

                
        btn_w = driver.find_element(By.CLASS_NAME, "btn_w")
        click_btn = btn_w.find_element(By.CLASS_NAME, "txt-center")
        
        time.sleep(2)
        media_count = driver.find_element(By.CLASS_NAME, "media-count").text
        match = re.search(r'\d{1,3}(,\d{3})*', media_count)
        if match:
            number = match.group().replace(',', '')
            range_count = int(number) / 9  # 한 페이지에서 보여지는 개수: 9개
            range_count = int(range_count)
            

        items_loaded = 0
        while items_loaded < range_count:
            print(f"Clicking {items_loaded + 1}/{range_count}")
            time.sleep(2)  # Click 전에 대기 시간을 조금 줄였습니다

            # 다시 ul을 찾음 (stale element 방지)
            ul = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "list-box")))
            
            time.sleep(2)  # Click 전에 대기 시간을 조금 줄였습니다
            lis = ul.find_elements(By.TAG_NAME, "li")[-9:]
            
            for li in lis:
                    a = li.find_element(By.TAG_NAME, "a")
                    list_img = a.find_element(By.CLASS_NAME, "list-img")
                    image_url = list_img.find_element(By.TAG_NAME, "img").get_attribute("src")

                    list_txt = a.find_element(By.CLASS_NAME, "list-txt")
                    ko_name = list_txt.find_element(By.CLASS_NAME, "tit-infotop").text  # 한문
                    en_name = list_txt.find_element(By.CLASS_NAME, "st-name").text  # 영문
                    step_txt = list_txt.find_element(By.CLASS_NAME, "step-txt").text  # Additional text

                    print("\n==============================================")
                    print("Image URL: ", image_url)
                    print("Chinese Name: ", ko_name)
                    print("English Name: ", en_name)
                    step_txt_arr = step_txt.split(">")
                    print("Step step_txt_arr: ", step_txt_arr)
                        
                    phylum_nm = step_txt_arr[0] if len(step_txt_arr) > 0 else '' # 문
                    class_nm = step_txt_arr[1] if len(step_txt_arr) > 1 else '' # 강
                    order_nm = step_txt_arr[2] if len(step_txt_arr) > 2 else '' # 목
                    family_nm = step_txt_arr[3] if len(step_txt_arr) > 3 else '' # 과
                    genus_nm = step_txt_arr[4] if len(step_txt_arr) > 4 else '' # 속

                    insert_sql = f'''
                            INSERT INTO tb_gt_biological_species (korNm, enNm, phylumNm, classnm, ordernm, familynm, genusnm, imageUrl)
                            VALUES ("{ko_name}", "{en_name}", "{phylum_nm}", "{class_nm}", "{order_nm}", "{family_nm}", "{genus_nm}", "{image_url}")
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

            conn.commit() 
            
            items_loaded += 1

            # 클릭 버튼을 다시 찾음 (stale element 방지)
            click_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "txt-center")))
            click_btn.click()
            time.sleep(2)  # 클릭 후 새로운 항목들이 로드될 시간을 기다림
   
    except NoAlertPresentException:
        pass
    except TimeoutException:
        pass
    except Exception as e:
        print(f"Error processing: {e}")
        
    finally:
        driver.quit()
        conn.close()

if __name__ == '__main__':
    main()