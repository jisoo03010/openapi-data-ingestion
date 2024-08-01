
import argparse
import configparser
import json
import requests
import urllib.parse
import configparser
import datetime
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
    
def api_url_query_params(api_name):
    api_name = api_name.upper()
    service_key = config.get(api_name, 'service_key')
    api_url = config.get(api_name, 'api_url')
    base_url = api_url.format(key=service_key)
    return base_url

def api_url_path_params(api_name, hydro_type, data_type, time_type, wlobscd, rfobscd, document_type):
    api_name = api_name.upper()
    if hydro_type == 'rainfall':
        service_key = config.get(api_name, 'rainfall_service_key')
        print("service_key L: ", service_key)
        api_url = config.get(api_name, 'api_url')
        base_url = api_url.format(
                                apiName=hydro_type,
                                key=service_key,
                                dataType=data_type,
                                timeType=time_type,
                                scd=rfobscd,
                                rType=document_type
                                )
    else:
        service_key = config.get(api_name, 'service_key')
        print("service_key L: ", service_key)
        api_url = config.get(api_name, 'api_url')
        base_url = api_url.format(
                                apiName=hydro_type,
                                key=service_key,
                                dataType=data_type,
                                timeType=time_type,
                                scd=wlobscd,
                                rType=document_type
                                )
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
    
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_WATER_QUALITY'
    columns_str = '''ptNo, ptNm, addr, orgNm, wmyr, wmod, wmwk, lonDgr, lonMin, lonSec, latDgr, latMin, latSec, wmcymd, wmdep, itemLvl, itemAmnt, itemTemp, itemPh, itemDoc, itemBod, itemCod, itemSs, itemTcoli, itemTn, itemTp, itemCd, itemCn, itemPb, itemCr6, itemAs, itemHg, itemCu, itemAbs, itemPcb, itemOp, itemMn, itemTrans, itemCloa, itemCl, itemZn, itemCr, itemFe, itemPhenol, itemNhex, itemEc, itemTce, itemPce, itemNo3n, itemNh3n, itemEcoli, itemPop, itemDtn, itemDtp, itemFl, itemCol, itemAlgol, itemCcl4, itemDceth, itemDcm,  itemBenzene, itemChcl3, itemToc, itemDehp, itemAntimon, itemDiox, itemHcho, itemHcb, itemNi, itemBa, itemSe''' #, createdAt, updatedAt 
    body = json_ob['getWaterMeasuringList']['item']
    response_data(body , table_name, columns_str)
    

# 수위 
def water_level(api_name, hydro_type, data_type, time_type, wlobscd, document_type):
    # water_level_rainfall, waterlevel, list, 10M, 10M, json
    final_url = api_url_path_params(api_name, hydro_type, data_type, time_type, wlobscd, "", document_type)
    json_ob = get_data_load(final_url)
    table_name  = 'TB_WATER_LEVEL'
    columns_str = '''wlobscd, ymdhm, wl, fw'''
    body = json_ob['content']
    response_data(body , table_name, columns_str)


# 강수량 rainfall(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
def rainfall(api_name, hydro_type, data_type, time_type, rfobscd, document_type):
    rfobscd = 10184100
    final_url = api_url_path_params(api_name, hydro_type, data_type, time_type, "", rfobscd, document_type)
    print("final_url : " , final_url)
    json_ob = get_data_load(final_url)
    table_name  = 'TB_RAINFALL'
    columns_str = '''rfobscd, ymdhm, rf'''
    body = json_ob['content']
    response_data(body , table_name, columns_str)
    
    
    
# 수위, 강수량 관측소 정보 조회 
def water_level_rainfall_sub(api_name, hydro_type):
    print("api_name ; ", api_name)
    final_url = api_url_path_params(api_name, hydro_type , "", "",  "", "", "")
    json_ob = get_data_load(final_url)
    
    if hydro_type == 'waterLevel':
        table_name  = 'TB_WATER_LEVEL_OBSERVATION_POINT' # 수위 관측소 정보 테이블
        columns_str = '''wlobscd, agcnm, obsnm, addr, etcaddr, lon, lat, gdt, attwl, wrnwl, almwl, srswl, pfh, fstnyn'''
    else:
        table_name  = 'TB_RAINFALL_OBSERVATION_POINT' # 강수량 관측소 정보 테이블
        columns_str = '''rfobscd, obsnm, agcnm, addr, etcaddr, lon, lat'''
        
    body = json_ob['content']
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
    
    
    # 수위, 강수량에 대한 서브 파서
    # python main.py water_level_rainfall --apiName=waterlevel
    water_level_rainfall_api = subparsers.add_parser('water_level_rainfall', help='water_level_rainfall')
    water_level_rainfall_api.add_argument('--apiName', default="", help="waterlevel or rainfall") # api 이름 선택 
    water_level_rainfall_api.add_argument('--dataType', default="list") # 단위 waterlevel or rainfall
    water_level_rainfall_api.add_argument('--timeType', default="10M", help="10M , 1H, 1D") #단위
    water_level_rainfall_api.add_argument('--wlobscd', default="3011665", help="관측소 코드") # 관측소 코드
    water_level_rainfall_api.add_argument('--sdt', default="", help="yyyyMMddHHmm, yyyyMMddHH, yyyyMMdd") # 시작시간
    water_level_rainfall_api.add_argument('--edt', default="", help="yyyyMMddHHmm, yyyyMMddHH, yyyyMMdd") # 종료 시간
    water_level_rainfall_api.add_argument('--rType', default="json", help="Format of the result (json or xml).") # return 타입
    
    
    # 수위, 강수량 관측소 정보 파서
    water_level_rainfall_sub_api = subparsers.add_parser('water_level_rainfall_sub', help='water_level_rainfall_sub')
    water_level_rainfall_sub_api.add_argument('--apiName', help="waterlevel or rainfall.") # return 타입
     
    return parser

if __name__ == '__main__':
    config = configparser.RawConfigParser(interpolation=None)
    config.read("config.ini", encoding="utf-8")
            
    parser = get_parser()
    args = parser.parse_args()

    if args.api == 'water_quality':
        water_quality(args.api, args.numOfRows, args.pageNo, args.resultType, args.wmyrList)
    elif args.api == 'water_level_rainfall': # 수위, 강수량 
        if args.apiName == "waterlevel":
            print("args.api :" , args.api)
            water_level(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
        elif args.apiName == "rainfall":
            rainfall(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
    elif args.api == "water_level_rainfall_sub": # 수위 강수량 관측소 정보  python main.py water_level_rainfall_sub --apiName=waterlevel
        water_level_rainfall_sub(args.api, args.apiName)

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
    
    
