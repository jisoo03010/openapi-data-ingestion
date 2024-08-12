
import argparse
import json
import requests
import urllib.parse
import configparser
import xml.etree.ElementTree as ET
import datetime
import pandas as pd
from database_connect import  save_to_database
# from water_quality import response_data
# 각 페이지에 필요한 파라미터 정보

def merge_data_frames(data_frames):
    # 데이터 프레임들을 수직 결합
    merged_df = pd.concat(data_frames, ignore_index=True, sort=False)
    print("merged_df : ", merged_df)
    if '사업장 소재지' in merged_df.columns.tolist():
        merged_df['사업장소재지'] = merged_df['사업장소재지'].combine_first(merged_df['사업장 소재지'])
        merged_df = merged_df.drop(columns=['사업장 소재지'])
    
    # '등록축종' 컬럼이 존재하는지 확인하고 결합
    if '등록축종' in merged_df.columns.tolist():
        merged_df['축종'] = merged_df['축종'].combine_first(merged_df['등록축종'])
        merged_df = merged_df.drop(columns=['등록축종'])
    
    
    # '데이터기준' 컬럼이 존재하는지 확인하고 결합
    if '데이터기준' in merged_df.columns.tolist():
        merged_df['데이터기준일자'] = merged_df['데이터기준일자'].combine_first(merged_df['데이터기준'])
        merged_df = merged_df.drop(columns=['데이터기준'])
        
    # '데이터기준' 컬럼이 존재하는지 확인하고 결합
    if '면적' in merged_df.columns.tolist():
        merged_df['사육면적'] = merged_df['사육면적'].combine_first(merged_df['면적'])
        merged_df = merged_df.drop(columns=['면적'])
        
    # '데이터기준' 컬럼이 존재하는지 확인하고 결합
    if '주사육업종' in merged_df.columns.tolist():
        merged_df['축종'] = merged_df['축종'].combine_first(merged_df['주사육업종'])
        merged_df = merged_df.drop(columns=['주사육업종'])
        
    if '연번' in merged_df.columns.tolist():
        merged_df = merged_df.drop(columns=['연번'])
        

    # data_frame_arr.append(data_frame)
    # merged_df = merge_data_frames(data_frame_arr)

    return merged_df

# url 통해 데이터 가져옴
def get_data_load(url):
    response = requests.get(url, verify=True , timeout=30)
    contents = response.text
    print(contents)
    json_ob = json.loads(contents)
    return json_ob
    
data_frame_arr = []

def response_data(body, table_name, columns_str):
    global data_frame_arr
    data_frame = pd.json_normalize(body)
    data_frame_arr.append(data_frame)
    merged_df = merge_data_frames(data_frame_arr)
    
    save_to_database(table_name, columns_str,  merged_df)
    
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
    table_name  = 'tb_gt_water_quality'
    columns_str = '''ptNo, ptNm, addr, orgNm, wmyr, wmod, wmwk, lonDgr, lonMin, lonSec, latDgr, latMin, latSec, wmcymd, wmdep, itemLvl, itemAmnt, itemTemp, itemPh, itemDoc, itemBod, itemCod, itemSs, itemTcoli, itemTn, itemTp, itemCd, itemCn, itemPb, itemCr6, itemAs, itemHg, itemCu, itemAbs, itemPcb, itemOp, itemMn, itemTrans, itemCloa, itemCl, itemZn, itemCr, itemFe, itemPhenol, itemNhex, itemEc, itemTce, itemPce, itemNo3n, itemNh3n, itemEcoli, itemPop, itemDtn, itemDtp, itemFl, itemCol, itemAlgol, itemCcl4, itemDceth, itemDcm,  itemBenzene, itemChcl3, itemToc, itemDehp, itemAntimon, itemDiox, itemHcho, itemHcb, itemNi, itemBa, itemSe''' #, createdAt, updatedAt 
    body = json_ob['getWaterMeasuringList']['item']
    response_data(body , table_name, columns_str)
    

# 수위 
def water_level(api_name, hydro_type, data_type, time_type, wlobscd, document_type):
    # water_level_rainfall, waterlevel, list, 10M, 10M, json
    final_url = api_url_path_params(api_name, hydro_type, data_type, time_type, wlobscd, "", document_type)
    json_ob = get_data_load(final_url)
    table_name  = 'tb_gt_water_level'
    columns_str = '''wlobscd, ymdhm, wl, fw'''
    body = json_ob['content']
    response_data(body , table_name, columns_str)


# 강수량 rainfall(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
def rainfall(api_name, hydro_type, data_type, time_type, rfobscd, document_type):
    rfobscd = 10184100
    final_url = api_url_path_params(api_name, hydro_type, data_type, time_type, "", rfobscd, document_type)
    json_ob = get_data_load(final_url)
    table_name  = 'tb_gt_rainfall'
    columns_str = '''rfobscd, ymdhm, rf'''
    body = json_ob['content']
    response_data(body , table_name, columns_str)
    
    
    
# 수위, 강수량 관측소 정보 조회 
def water_level_rainfall_sub(api_name, hydro_type):
    final_url = api_url_path_params(api_name, hydro_type , "", "",  "", "", "")
    json_ob = get_data_load(final_url)
    
    if hydro_type == 'waterlevel':
        table_name  = 'tb_gt_water_level_observation_point' # 수위 관측소 정보 테이블
        columns_str = '''wlobscd, agcnm, obsnm, addr, etcaddr, lon, lat, gdt, attwl, wrnwl, almwl, srswl, pfh, fstnyn'''
    elif hydro_type == 'rainfall':
        table_name  = 'tb_gt_rainfall_observation_point' # 강수량 관측소 정보 테이블
        columns_str = '''rfobscd,  agcnm ,obsnm, addr, etcaddr, lon, lat'''
        
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
    table_name  = 'tb_gt_weather'
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

    
    json_ob = get_data_load(final_url)
    table_name  = 'tb_gt_atmosphere'
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
    table_name  = 'tb_gt_atmosphere_observation_point'
    columns_str = '''dmX, item,  mangName,  year, addr, stationName, dmY''' #, createdAt, updatedAt 
    body = json_ob['response']['body']['items']
    response_data(body , table_name, columns_str)



# xml 처리 ------------------------------
def clean_text(text):
    if text:
        return text.replace('<![CDATA[', '').replace(']]>', '').replace('<', '').replace('>', '').replace('!', '').replace('[', '').replace(']', '')
    return text

def xml_to_dict(element):
    if len(element) == 0:
        return clean_text(element.text)
    result_dict = {}
    for child in element:
        if child.tag == "item":
            if "items" not in result_dict:
                result_dict["items"] = []
            result_dict["items"].append(xml_to_dict(child))
        else:
            result_dict[child.tag] = xml_to_dict(child)
    return result_dict
        
# 문화재 func
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
    
    response = requests.get(final_url, verify=False)
    xml_data = response.text
    
    root = ET.fromstring(xml_data)
    data_dict = {root.tag: xml_to_dict(root)}
    # Convert dictionary to JSON
    json_data = json.dumps(data_dict, ensure_ascii=False, indent=4)
    
    json_ob = json.loads(json_data)
    table_name  = 'tb_gt_cultural'
    columns_str = ''' no, ccmaName, ccbaMnm1, ccbaMnm2, ccbaCtcdNm, ccsiName, ccbaAdmin, ccbaKdcd, ccbaCtcd, ccbaAsno, ccbaCncl, ccbaCpno, longitude, latitude, regDt''' #, createdAt, updatedAt 
    body = json_ob['result']['items']
    for i in range(len(body)):
        print("ccbaKdcd : ", body[i]['ccbaKdcd'])
        cultural_img(body[i]['ccbaAsno'],  body[i]['ccbaKdcd'])

    response_data(body , table_name, columns_str)
            
    # cultural_img(ccba_kdcd, ccba_asno, ccba_ctcd)

# # 문화재 이미지 func
def cultural_img(ccba_asno , ccba_kdcd): #종목코드, 관리번호, 시도코드
    # ccba_kdcd = [11, 12,  13, 14, 15, 16, 17, 18, 21, 22, 23, 24, 25, 31, 79, 80]
    
    query_params = {
        # 'api': 'cultural_img',
        'ccbaKdcd': ccba_kdcd,
        'ccbaAsno': ccba_asno,
        'ccbaCtcd': '33'
    }
    print(" \n\n query_params : ",query_params)
    base_url = api_url_query_params('cultural_image')
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)
    response = requests.get(final_url, verify=False)
    xml_data = response.text
    root = ET.fromstring(xml_data)
    data_dict = {root.tag: xml_to_dict(root)}
    # Convert dictionary to JSON
    json_data = json.dumps(data_dict, ensure_ascii=False, indent=4)
    
    json_ob = json.loads(json_data)
    table_name  = 'tb_gt_cultural_img'
    columns_str = '''imageNuri, imageUrl, ccimDesc''' #, createdAt, updatedAt 
    body = json_ob['result']['items']
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
    table_name  = 'tb_gt_tourism'
    columns_str = '''zip, areaSe, lng, thumbImg, regDate, tourImg, hmpg, telno, tourSe, tourNm, mobileTelno, tourUrl, adres, tourNo, lat, operTime, intrcn''' #, createdAt, updatedAt 
    body = json_ob['result']
    response_data(body , table_name, columns_str)

def farminfo(api_name, page, per_page, return_type):
    query_params = {
        'api': api_name,
        'page': page,  
        'perPage': per_page,
        'returnType': return_type
    }
    
    api_name = api_name.upper()
    service_key = config.get(api_name, 'service_key')
    arr = ['jincheon', 'jeungpyeong', 'eumseong', 'goesan', 'cheongju']
    table_name  = 'tb_gt_farminfo'
    columns_str = '''farmName, BusinessAddress, farmArea, livestockType, dataReferenceDate, numberOfLivestock, animalCount, roadAddress, lotAddress, category''' #, createdAt, updatedAt 
    
    for i in arr:
        i += '_api_url'
        api_url = config.get(api_name, i)
        base_url = api_url.format(key=service_key)
    
        url_parts = list(urllib.parse.urlparse(base_url))
        query = urllib.parse.parse_qs(url_parts[4])
        query.update(query_params)
    
        url_parts[4] = urllib.parse.urlencode(query, doseq=True)
        final_url = urllib.parse.urlunparse(url_parts)
    
        json_ob = get_data_load(final_url)
        body = json_ob['data']
        response_data(body , table_name, columns_str)
        
        
        
def biological_species(api_name, page_index):
    query_params = {
        'pageIndex': page_index
    }
    base_url = api_url_query_params(api_name)
    url_parts = list(urllib.parse.urlparse(base_url))
    query = urllib.parse.parse_qs(url_parts[4])
    query.update(query_params)
    
    url_parts[4] = urllib.parse.urlencode(query, doseq=True)
    final_url = urllib.parse.urlunparse(url_parts)

    # json_ob = get_data_load(final_url)
    response = requests.get(final_url,  timeout=30)
    contents = response.text
    print(contents)
    # table_name  = 'tb_gt_weather'
    # columns_str = '''baseDate, baseTime, category, fcstDate, fcstTime, fcstValue, nx, ny ''' #, createdAt, updatedAt 
    # body = json_ob['item']
    # print("\n\n\nbody ::::::::::::::::::::::::::::::::::::::::::::::", body)
    # response_data(body , table_name, columns_str)
    
def biological_detail(api_name, ktsn):
    query_params = {
        'ktsn': ktsn
    }
    print("query_params : ", query_params , api_name)

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
    
    
    # 문화재 정보 파서 (xml 전처리 필요)
    cultural_api = subparsers.add_parser('cultural', help='cultural')
    cultural_api.add_argument('--ccbaCtcd', default="33",  help="")
    cultural_api.add_argument('--ccbaKdcd', default="",  help="")
    cultural_api.add_argument('--pageUnit', default="1000",  help="")
    
    # 문화재 이미지 정보 파서 (xml 전처리 필요)
    # cultural_image_api = subparsers.add_parser('cultural_img', help='cultural_img')
    # cultural_image_api.add_argument('--ccbaCtcd', default="33",  help="")
    # cultural_image_api.add_argument('--ccbaKdcd', default="",  help="")
    # cultural_image_api.add_argument('--ccbaAsno', default="",  help="")
    
    # 축산시설정보 외 ,,,5개 파서
    farminfo_api = subparsers.add_parser('farminfo', help='farminfo')
    farminfo_api.add_argument('--page', default="1",  help="")
    farminfo_api.add_argument('--perPage', default="2000",  help="") # totalCount
    farminfo_api.add_argument('--returnType', default="json",  help="")
    # farminfo_api.add_argument('--region', default="",  help="지역명 영문으로 작성해주세요. \n ex : (jincheon, jeungpyeong, eumseong, goesan, cheongju)") 
    
    
    
    # 관광지 정보 파서
    tourism_api = subparsers.add_parser('tourism', help='tourism')
    tourism_api.add_argument('--pageUnit', default="2000",  help="") # totalCount
    tourism_api.add_argument('--searchCnd', default="tourNm",  help="")
    tourism_api.add_argument('--searchKrwd', default="",  help="") # 청주 (필수x)
    
    
    # 국가생물종 정보 파서
    biological = subparsers.add_parser('biological', help='biological')
    biological.add_argument('--pageIndex', default=1,  help="") # 총 6001페이지
    biological.add_argument('--userId', default=config.get('BIOLOGICAL', 'user_id'))
    
    
    biological_detail = subparsers.add_parser('biological_detail', help='biological_detail')
    biological_detail.add_argument('--ktsn') 
    biological.add_argument('--userId', default=config.get('BIOLOGICAL', 'user_id'))
    
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
            water_level(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
            
        elif args.apiName == "rainfall":
            rainfall(args.api, args.apiName, args.dataType, args.timeType, args.wlobscd, args.rType)
    
    elif args.api == "water_level_rainfall_sub": # 수위 강수량 관측소 정보  python main.py water_level_rainfall_sub --apiName=waterlevel
        water_level_rainfall_sub(args.api, args.apiName)
        
    # 페이지 모듈 별 정보 
    elif args.api == "weather": # 기상 정보
        weather(args.api, args.pageNo,  args.numOfRows, args.dataType, args.base_date, args.base_time, args.nx, args.ny)
        
    elif args.api == "atmoshpere": # 대기 정보
        atmoshpere(args.api, args.sidoName, args.numOfRows, args.pageNo, args.ver, args.returnType)
        
    elif args.api == "atmoshpere_sub": # 대기 관측소 정보
        atmoshpere_sub(args.api, args.numOfRows,  args.pageNo, args.stationName, args.addr, args.returnTypeSub)
        
    elif args.api == "cultural": # 문화재 정보 (xml 변환 필요)
        cultural(args.api, args.ccbaCtcd, args.ccbaKdcd, args.pageUnit)
        
    # elif args.api == "cultural_img": # 문화재 이미지 정보  (xml 변환 필요)
    #     cultural_img(args.api, args.ccbaCtcd)
        
    elif args.api == "tourism": # 관광지 정보
        tourism(args.api, args.pageUnit, args.searchCnd, args.searchKrwd )
        
    elif args.api == "farminfo": # 축산시설 정보
        farminfo(args.api, args.page, args.perPage, args.returnType )
        
    elif args.api == "biological": # 국가생물종 
        # biological_species(args.api, args.pageIndex, args.userId)
        biological_species(args.api, args.pageIndex)
        
    elif args.api == "biological_detail": # 국가생물종 상세
        biological_detail(args.api, args.ktsn)
        
