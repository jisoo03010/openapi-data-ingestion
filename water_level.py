import json
import pandas as pd
from database_connect import save_to_database
import requests
import argparse
import urllib.parse

import configparser as parser 
import configparser
import re
import configparser
# # 수위
# def get_data_load(url):
#     response = requests.get(url)
#     contents = response.text
#     json_ob = json.loads(contents)
#     response_data(json_ob)

# https://api.hrfco.go.kr/8E463C92-7953-4C11-A636-9A7A6670D966/waterlevel/list/10M/3011665/202407028410/202407291120.json
def response_data(json_ob):
    body = json_ob['content']
    data_frame = pd.json_normalize(body)
    table_name  = 'TB_WATER_QUALITY_OBSERVATION_POINT' #수위 테이블 
    columns_str = '''wlobscd, ymdhm, wl, fw, links'''
    save_to_database(table_name, columns_str,  data_frame)
    
    
if __name__ == '__main__':
    print("wate 실행 ")
    # parser = argparse.ArgumentParser(description='Add some integers.')
    # parser.add_argument('--url', default="", help="Number of rows to retrieve.")
    
    # config = configparser.RawConfigParser(interpolation=None)
    # config.read("config.ini", encoding="utf-8")
                
    # 서울시(한강대교) 10분 기간별 자료 :
    # https://api.hrfco.go.kr/ServiceKey/waterlevel/list/10M/1018683/202407301100/202407311100.xml
    
    # URL 구성 파라미터 
    # parser.add_argument('--hydroType', default="waterlevel", help="waterlevel or rainfall") # 단위 waterlevel or rainfall
    # parser.add_argument('--dataType', default="list") # 단위 waterlevel or rainfall
    # parser.add_argument('--timeType', default="10M", help="10M , 1H, 1D") #단위
    # parser.add_argument('--wlobscd', default="1", help="Page number to retrieve.") # 관측소 코드
    # parser.add_argument('--sdt', default="json", help="") # 시작시간
    # parser.add_argument('--edt', default="2024", help="Year list for water measurements.") # 종료 시간
    # parser.add_argument('--rType', default="json", help="Format of the result (json or xml).") # return 타입
    
    # args = parser.parse_args()
    
    
    
    # query_params = {
    #     'numOfRows': args.numOfRows,
    #     'pageNo': args.pageNo,
    #     'resultType': args.resultType,
    #     'wmyrList': args.wmyrList
    # }
    
    # service_key = config.get("WATER_QUALITY", 'service_key')
    # api_url = config.get("WATER_QUALITY", 'api_url')
    # base_url = f"{api_url}?serviceKey={service_key}"
    
    # url_parts = list(urllib.parse.urlparse(base_url))
    # query = urllib.parse.parse_qs(url_parts[4])
    # query.update(query_params)
    # url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    # final_url = urllib.parse.urlunparse(url_parts)
    
    # # 결과 출력
    # print(f"Final URL: {final_url}")
    # get_data_load(final_url)
    
    
    
    
    
    
    
    
    
# def db_connect():
#     db_user = config.get('DATABASE', 'db_user')
#     db_password = config.get('DATABASE', 'db_password')
#     db_host = config.get('DATABASE', 'db_host')
#     db_port = config.getint('DATABASE', 'db_port')
#     db_database = config.get('DATABASE', 'db_database')


#     try:
#         conn = pymysql.connect(
#  user=db_user,
#  password=db_password,
#             host=db_host,
#             port=db_port,
#             database=db_database
#         )
#     except pymysql.Error as e:
#         print(f"Error connecting to MySQL DB: {e}")
        
        
#     cursor = conn.cursor()
    
#     return cursor , conn

# def save_to_database(dataframe):
#     # NaN 값을 None으로 변환
#     dataframe = dataframe.where(pd.notnull(dataframe), "None")
#     cursor , conn = db_connect()
    
#     # v
#     try:
        
#         query = '''
#             INSERT INTO TB_WATER_QUALITY (
#                 rowno, ptNo, ptNm, addr, orgNm, wmyr, wmod, wmwk, lonDgr, lonMin, lonSec,
#                 latDgr, latMin, latSec, wmcymd, wmdep, itemLvl, itemAmnt, itemTemp, itemPh,
#                 itemDoc, itemBod, itemCod, itemSs, itemTcoli, itemTn, itemTp, itemCd, itemCn,
#                 itemPb, itemCr6, itemAs, itemHg, itemCu, itemAbs, itemPcb, itemOp, itemMn,
#                 itemTrans, itemCloa, itemCl, itemZn, itemCr, itemFe, itemPhenol, itemNhex,
#                 itemEc, itemTce, itemPce, itemNo3n, itemNh3n, itemEcoli, itemPop, itemDtn,
#                 itemDtp, itemFl, itemCol, itemAlgol, itemCcl4, itemDceth, itemDcm, itemBenzene,
#                 itemChcl3, itemToc, itemDehp, itemAntimon, itemDiox, itemHcb, itemNi, itemBa,
#                 itemSe, created_at, updated_at
#         ) VALUES (
#         ''' 
#         for _, row in dataframe.iterrows():
            
#             cursor.execute(query, (
#             row['ROWNO'], row['PT_NO'], row['PT_NM'], row['ADDR'], row['ORG_NM'], row['WMYR'], row['WMOD'], row['WMWK'], row['LON_DGR'], row['LON_MIN'], row['LON_SEC'],
#             row['LAT_DGR'], row['LAT_MIN'], row['LAT_SEC'], row['WMCYMD'], row['WMDEP'], row['ITEM_LVL'], row['ITEM_AMNT'], row['ITEM_TEMP'],
#             row['ITEM_PH'], row['ITEM_DOC'], row['ITEM_BOD'], row['ITEM_COD'], row['ITEM_SS'], row['ITEM_TCOLI'], row['ITEM_TN'], row['ITEM_TP'], row['ITEM_CD'],
#             row['ITEM_CN'], row['ITEM_PB'], row['ITEM_CR6'], row['ITEM_AS'], row['ITEM_HG'], row['ITEM_CU'], row['ITEM_ABS'], row['ITEM_PCB'], row['ITEM_OP'], row['ITEM_MN'], row['ITEM_TRANS'], row['ITEM_CLOA'], row['ITEM_CL'], row['ITEM_ZN'], row['ITEM_CR'], row['ITEM_FE'], row['ITEM_PHENOL'], row['ITEM_NHEX'], row['ITEM_EC'],
#             row['ITEM_TCE'], row['ITEM_PCE'], row['ITEM_NO3N'], row['ITEM_NH3N'], row['ITEM_ECOLI'], row['ITEM_POP'], row['ITEM_DTN'], row['ITEM_DTP'], row['ITEM_FL'], row['ITEM_COL'], row['ITEM_ALGOL'], row['ITEM_CCL4'], row['ITEM_DCETH'], row['ITEM_DCM'], row['ITEM_BENZENE'],
#             row['ITEM_CHCL3'], row['ITEM_TOC'], row['ITEM_DEHP'], row['ITEM_ANTIMON'], row['ITEM_DIOX'], row['ITEM_HCB'], row['ITEM_NI'], row['ITEM_BA'], row['ITEM_SE'], datetime.now(), datetime.now()
#         ))
        
#         conn.commit()
#         print("성공적으로 데이터가 삽입되었습니다.!")
        
#     except pymysql.Error as e:
#         print(f"Error inserting data: {e}")
#         conn.rollback()

#     finally:
#         conn.close()

# if __name__ == '__main__':
    
    
#     config = configparser.RawConfigParser()
#     config.read("config.ini")
#     service_key = config.get('SERVICE_KEY', 'water_quality_service_key')

        
    # parser = argparse.ArgumentParser(description='Add some integers.')
    # parser.add_argument('--serviceKey', default="d4Tv3fhoFt08iCetWmvZ7ePHLPJoTLK38nF5bIg6%2FiqeTGEPnSAQZc4lSfm6yKJxETYjwXei%2B%2BT0rlQD05sM9w%3D%3D", help="Issue a service key.")
#     parser.add_argument('--numOfRows', default="1", help="Number of rows to retrieve.")
#     parser.add_argument('--pageNo', default="1", help="Page number to retrieve.")
#     parser.add_argument('--resultType', default="json", help="Format of the result (json or xml).")
#     parser.add_argument('--wmyrList', default="2024", help="Year list for water measurements.")
#     args = parser.parse_args()
    
#     url = f"http://apis.data.go.kr/1480523/WaterQualityService/getWaterMeasuringList?serviceKey={service_key}&numOfRows={args.numOfRows}&pageNo={args.pageNo}&resultType={args.resultType}&wmyrList={args.wmyrList}&ptNoList=3011A05,3011A10,3011A20,3011A25,3011A30,3011A32,3011A35,3011A40,3011A45,3011A50,3011A60,3011A65,3011A70,3011A80,3011A82,3011A85,3011A90,3011A97,3011D05,3011D10,3011D15,3011D20,3011D25,3011D30,3011D35,3011D40,3011D45,3011D46,3011D50,3011D55,3011D60,3011D65,3011D70,3011D75,3011D80,3011D85,3011D90,3011E11,3011E15,3011E31,3011E40,3011A15,3011A17,3011A43,3011A48,3011A53,3011A68,3011A78,3011A79,3011A84,3011A87"

#     # total_count = get_data_load(url)
#     response = requests.get(url)
#     json_ob = json.loads(response.text)
#     total_count = json_ob['getWaterMeasuringList']['totalCount'] # 전체 데이터 개수
#     print(f"\n\n\n\n전체 데이터 개수 : {url}\n\n\n\n")
#     setting_url = f"http://apis.data.go.kr/1480523/WaterQualityService/getWaterMeasuringList?serviceKey={service_key}&numOfRows={total_count}&pageNo={args.pageNo}&resultType={args.resultType}&wmyrList={args.wmyrList}&ptNoList=3011A05,3011A10,3011A20,3011A25,3011A30,3011A32,3011A35,3011A40,3011A45,3011A50,3011A60,3011A65,3011A70,3011A80,3011A82,3011A85,3011A90,3011A97,3011D05,3011D10,3011D15,3011D20,3011D25,3011D30,3011D35,3011D40,3011D45,3011D46,3011D50,3011D55,3011D60,3011D65,3011D70,3011D75,3011D80,3011D85,3011D90,3011E11,3011E15,3011E31,3011E40,3011A15,3011A17,3011A43,3011A48,3011A53,3011A68,3011A78,3011A79,3011A84,3011A87"
#     get_data_load(setting_url)
    
    