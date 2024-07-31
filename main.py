
import argparse
import configparser
import re
import json
import requests
import urllib.parse
import configparser
import subprocess

import pandas as pd
from database_connect import save_to_database
from water_quality import response_data
# 각 페이지에 필요한 파라미터 정보



# url 통해 데이터 가져옴
def get_data_load(url):
    response = requests.get(url)
    contents = response.text
    json_ob = json.loads(contents)
    return json_ob
    

def response_data(body , table_name, columns_str):
    data_frame = pd.json_normalize(body)
    save_to_database(table_name, columns_str,  data_frame)
    
def api_url(api_name):
    api_name = api_name.upper()
    service_key = config.get(api_name, 'service_key')
    api_url = config.get(api_name, 'api_url')
    base_url = api_url.format(key=service_key)
    return base_url






# OpenAPI 별 지정 값
# - service_key : API 서비스 키
# - query_params : API 호출 시 필요한 파라미터 정보
# - table_name : 테이블 명 
# - columns_str : 테이블 컬럼명 (지정하는 이유: API 호출 시 키 값으로 가져올 수도 있었으나, 특정 몇몇 API의 키 값이 한국어로 되어 있어 영문으로 직접 지정하여 구현하였음.)
# - body : API 호출 시 필요한 body 정보 (API마다 가져오려는 상위 키 값의 이름이 다름)
# - subparsers : 요청하려는 API에 대해 상세 조회를 수행할 때 필요한 파라미터를 받기 위한 설정을 구성


# 수질 데이터
def water_quality(api_name, num_of_rows, page_no, result_type, wmyr_list):
    query_params = {
        'numOfRows': num_of_rows, 
        'pageNo': page_no,
        'resultType': result_type,
        'wmyrList': wmyr_list
    }
    
    base_url = api_url(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_WATER_QUALITY'
    columns_str = '''ptNo, ptNm, addr, orgNm, wmyr, wmod, wmwk, lonDgr, lonMin, lonSec, latDgr, latMin, latSec, wmcymd, wmdep, itemLvl, itemAmnt, itemTemp, itemPh, itemDoc, itemBod, itemCod, itemSs, itemTcoli, itemTn, itemTp, itemCd, itemCn, itemPb, itemCr6, itemAs, itemHg, itemCu, itemAbs, itemPcb, itemOp, itemMn, itemTrans, itemCloa, itemCl, itemZn, itemCr, itemFe, itemPhenol, itemNhex, itemEc, itemTce, itemPce, itemNo3n, itemNh3n, itemEcoli, itemPop, itemDtn, itemDtp, itemFl, itemCol, itemAlgol, itemCcl4, itemDceth, itemDcm,  itemBenzene, itemChcl3, itemToc, itemDehp, itemAntimon, itemDiox, itemHcho, itemHcb, itemNi, itemBa, itemSe, createdAt, updatedAt '''
    body = json_ob['getWaterMeasuringList']['item']
    response_data(body , table_name, columns_str)
    

def water_level(api_name, hydro_type, data_type, time_type, wlobscd, sdt, edt, document_type):
    query_params ={
        "HydroType": hydro_type,
        "DataType": data_type,
        "TimeType": time_type,
        "Wlobscd":wlobscd,
        "Sdt": sdt,
        "Edt": edt,
        "DocumentType" : document_type
    }
    base_url = api_url(api_name)
    
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_WATER_LEVEL'
    columns_str = '''wlobscd, ymdhm, wl, fw, links'''
    body = json_ob['getWaterMeasuringList']['item']
    response_data(body , table_name, columns_str)
    
    
def get_parser():
    parser = argparse.ArgumentParser(description='API별 크롤링 및 파라미터 처리')
    subparsers = parser.add_subparsers(dest='api', help='API 이름을 지정하세요.')
    
    # water_quality_api에 대한 서브 파서
    water_quality_api = subparsers.add_parser('water_quality', help='water_quality_api')
    water_quality_api.add_argument('--numOfRows', default="239", help="Number of rows to retrieve.")
    water_quality_api.add_argument('--pageNo', default="1", help="Page number to retrieve.")
    water_quality_api.add_argument('--resultType', default="json", help="Format of the result (json or xml).")
    water_quality_api.add_argument('--wmyrList', default="2024", help="Year list for water measurements.")
    
    
    # water_level_api에 대한 서브 파서
    water_level_api = subparsers.add_parser('water_level', help='water_level_api')
    water_level_api.add_argument('--HydroType', default="", help="")
    water_level_api.add_argument('--DataType', default="", help="")
    water_level_api.add_argument('--TimeType', default="", help="")
    water_level_api.add_argument('--Wlobscd', default="", help="")
    water_level_api.add_argument('--Sdt', default="", help="")
    water_level_api.add_argument('--Edt', default="", help="")
    water_level_api.add_argument('--DocumentType', default="json", help="")
    
    return parser

if __name__ == '__main__':
    config = configparser.RawConfigParser(interpolation=None)
    config.read("config.ini", encoding="utf-8")
            
    parser = get_parser()
    args = parser.parse_args()

    # pageName = args.pageName.upper()
    if args.api == 'water_quality':
        print("args.api : " , args.api )
        print("args.numOfRows : " , args.numOfRows )
        print("args.pageNo : " , args.pageNo )
        print("args.resultType :" ,args.resultType )
        print("args.wmyrList : " , args.wmyrList )
        water_quality(args.api, args.numOfRows, args.pageNo, args.resultType, args.wmyrList)
    elif args.api == 'water_level':
        print("water_level start")
        
    
        # water_level(args.api, args.numOfRows, args.pageNo, args.resultType, args.wmyrList)
        
    # 페이지 모듈 별 정보 
    # if config.has_section(pageName):
        
        # 서비스 키, api_url 가져오기 
        # service_key = config.get(pageName, 'service_key')
        # api_url = config.get(pageName, 'api_url')
        # url = f"{api_url}?serviceKey={service_key}"
        
        # command = ["python", f"{args.pageName}.py", f"--url={url}"]
        
    #     command = ["python", f"{args.pageName}.py"]
    #     # 명령어 실행
    #     subprocess.run(command, shell=True)
    # else:
    #     print(f"Configuration for page {args.pageName} not found.")
    
    
