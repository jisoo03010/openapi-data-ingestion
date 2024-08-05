
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
    response = requests.get(url, verify=False)
    contents = response.text
    json_ob = json.loads(contents)
    return json_ob
    

def response_data(body , table_name, columns_str):
    data_frame = pd.json_normalize(body)
    
    save_to_database(table_name, columns_str,  data_frame)
    
def api_url_query_params(api_name):
    api_name = api_name.upper()
    api_url = config.get(api_name, 'api_url')
    if config.get(api_name, 'service_key') == "":
        return api_url
    else :
        service_key = config.get(api_name, 'service_key')
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
    
    
# 기상 데이터 args.api, args.pageNo,  args.numOfRows, args.dataType,
# args.baseDate, args.baseTime, args.nx, args.ny
def weather(api_name, page_no, num_of_rows, data_type, base_date, base_time, nx, ny):
    query_params = {
        'pageNo': page_no,
        'numOfRows': num_of_rows,  
        'dataType': data_type,
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)

    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_WEATHER'
    columns_str = '''baseDate, baseTime, category, fcstDate, fcstTime, fcstValue, nx, ny ''' #, createdAt, updatedAt 
    body = json_ob['response']['body']['items']['item']
    response_data(body , table_name, columns_str)
    
    
def atmoshpere(api_name, sido_name, num_of_rows, page_no, ver, return_type):
    query_params = {
        'numOfRows': num_of_rows,
        'pageNo': page_no,  
        'sidoName': sido_name,
        'ver': ver,
        'returnType': return_type
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)

    
    print("final_url : ", final_url)
    json_ob = get_data_load(final_url)
    print("json_ob : ", json_ob)
    table_name  = 'TB_ATMOSPHERE'
    columns_str = '''so2Grade, coFlag, khaiValue, so2Value, coValue, pm25Flag, pm10Flag, pm10Value, o3Grade, khaiGrade, pm25Value, sidoName, no2Flag, no2Grade, o3Flag, pm25Grade, so2Flag, dataTime, coGrade, no2Value, stationName, pm10Grade, o3Value''' #, createdAt, updatedAt 
    body = json_ob['response']['body']['items']
    response_data(body , table_name, columns_str)
    
    
    
def atmoshpere_sub(api_name, num_of_rows, page_no, station_name, addr, return_type):
    query_params = {
        'numOfRows': num_of_rows,
        'pageNo': page_no,  
        'addr': addr,  
        'stationName': station_name,
        'returnType': return_type
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_ATMOSPHERE_OBSERVATION_POINT'
    columns_str = '''dmX, item,  mangName,  year, addr, stationName, dmY''' #, createdAt, updatedAt 
    body = json_ob['response']['body']['items']
    response_data(body , table_name, columns_str)
    
    
        
def cultural(api_name, ccba_ctcd, ccba_kdcd, page_unit):
    query_params = {
        'api': api_name,
        'ccbaCtcd': ccba_ctcd,  
        'ccbaKdcd': ccba_kdcd,  
        'pageUnit': page_unit
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    print("final_url:", final_url)
    json_ob = get_data_load(final_url)
    table_name  = 'TB_CULTURAL'
    columns_str = ''' no, ccmaName, ccbaMnm1, ccbaMnm2, ccbaCtcdNm, ccsiName, ccbaAdmin, ccbaKdcd, ccbaCtcd, ccbaAsno, ccbaCncl, ccbaCpno, longitude, latitude, regDt''' #, createdAt, updatedAt 
    body = json_ob['result']
    response_data(body , table_name, columns_str)
    
def tourism(api_name, page_unit, search_cnd, search_krwd):
    query_params = {
        'api': api_name,
        'pageUnit': page_unit,  
        'searchCnd': search_cnd,
        'searchKrwd': search_krwd
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    
    json_ob = get_data_load(final_url)
    table_name  = 'TB_TOURISM'
    columns_str = '''zip, areaSe, lng, thumbImg, regDate, tourImg, hmpg, telno, tourSe, tourNm, mobileTelno, tourUrl, adres, tourNo, lat, operTime, intrcn''' #, createdAt, updatedAt 
    body = json_ob['result']
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
    
    
    # 수위, 강수량에 대한 서브 파서j
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
     
    # 기상 정보 파서
    now = datetime.datetime.now()
    two_days_ago = now - datetime.timedelta(days=1)
    formatted_date = two_days_ago.strftime('%Y%m%d')
    weather_api = subparsers.add_parser('weather', help='weather')
    weather_api.add_argument('--pageNo',    default="1",    help="") # 페이지 번호 
    weather_api.add_argument('--numOfRows', default="1000",  help="") # 한 페이지 결과 수 
    weather_api.add_argument('--dataType',  default="json", help="") # 응답자료형식 
    weather_api.add_argument('--base_date',  default=formatted_date,    help="") # 발표일자(필수) (3일 전 데이터까지만 보여줄 수 있음.)
    weather_api.add_argument('--base_time',  default="1000",    help="") # 발표시각(필수) 
    weather_api.add_argument('--nx',        default="36",    help="") # 예보지점 X 좌표(필수) 
    weather_api.add_argument('--ny',        default="127",    help="") # 예보지점 Y 좌표(필수) 
    
    # 대기 정보 파서
    atmoshpere_api = subparsers.add_parser('atmoshpere', help='atmoshpere')
    atmoshpere_api.add_argument('--sidoName', default="충북",  help="")
    atmoshpere_api.add_argument('--numOfRows', default="100",  help="")
    atmoshpere_api.add_argument('--pageNo', default="1",  help="")
    atmoshpere_api.add_argument('--returnType', default="json",  help="")
    atmoshpere_api.add_argument('--ver', default="1.0",  help="")
    
    # 대기 측정소 정보 파서
    atmoshpere_sub_api = subparsers.add_parser('atmoshpere_sub', help='atmoshpere_sub')
    atmoshpere_sub_api.add_argument('--numOfRows', default="100",  help="")
    atmoshpere_sub_api.add_argument('--pageNo', default="1",  help="")
    atmoshpere_sub_api.add_argument('--addr', default="충북",  help="")
    atmoshpere_sub_api.add_argument('--returnTypeSub', default="json",  help="")
    atmoshpere_sub_api.add_argument('--stationName', default="",  help="")
    
    
    # 문화재 정보 파서
    cultural_api = subparsers.add_parser('cultural', help='cultural')
    cultural_api.add_argument('--ccbaCtcd', default="33",  help="")
    cultural_api.add_argument('--ccbaKdcd', default="11",  help="")
    cultural_api.add_argument('--pageUnit', default="300",  help="")
    
    # 문화재 이미지 정보 파서
    cultural_image_api = subparsers.add_parser('cultural_img', help='cultural_img')
    cultural_image_api.add_argument('--ccbaCtcd', default="33",  help="")
    cultural_image_api.add_argument('--ccbaKdcd', default="11",  help="")
    cultural_image_api.add_argument('--ccbaAsno', default="00640000",  help="")
    
    # 축산시설정보 외 ,,,5개 파서
    
    
    
    
    
    
    
    
    # 관광지 정보 파서
    tourism_api = subparsers.add_parser('tourism', help='tourism')
    tourism_api.add_argument('--pageUnit', default="2000",  help="") # totalCount
    tourism_api.add_argument('--searchCnd', default="tourNm",  help="")
    tourism_api.add_argument('--searchKrwd', default="",  help="") # 청주 (필수x)
    
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
        
    # 페이지 모듈 별 정보 
    elif args.api == "weather": # 수위 강수량 관측소 정보  python main.py water_level_rainfall_sub --apiName=waterlevel
        weather(args.api, args.pageNo,  args.numOfRows, args.dataType, args.base_date, args.base_time, args.nx, args.ny)
        
    elif args.api == "atmoshpere": # 대기 정보
        atmoshpere(args.api, args.sidoName, args.numOfRows, args.pageNo, args.ver, args.returnType)
        
    elif args.api == "atmoshpere_sub": # 대기 관측소 정보
        atmoshpere_sub(args.api, args.numOfRows,  args.pageNo, args.stationName, args.addr, args.returnTypeSub)
        
    elif args.api == "cultural": # 문화재 정보 (xml 변환 필요)
        cultural(args.api, args.ccbaCtcd, args.ccbaKdcd, args.pageUnit)
        
    # elif args.api == "cultural_img": # 문화재 이미지 정보  (xml 변환 필요)
    #     cultural_img(args.api, )
        
    elif args.api == "tourism": # 관광지 정보
        tourism(args.api, args.pageUnit, args.searchCnd, args.searchKrwd )
        
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
    
    
