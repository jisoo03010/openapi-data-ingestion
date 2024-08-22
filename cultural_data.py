

import xml.etree.ElementTree as ET
import json
from collections import defaultdict

# XML 데이터 문자열
xml_data = '''<?xml version="1.0" encoding="utf-8"?>
<result>
    <totalCnt>6</totalCnt>
    <ccbaKdcd>11</ccbaKdcd>
    <ccbaAsno>00060000</ccbaAsno>
    <ccbaCtcd>33</ccbaCtcd>
    <ccbaMnm1>
        <![CDATA[충주 탑평리 칠층석탑]]>
    </ccbaMnm1>
    <ccbaMnm2>
        <![CDATA[忠州 塔坪里 七層石塔]]>
    </ccbaMnm2>
    <item>
        <sn>1</sn>
        <imageNuri>D</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612144.jpg</imageUrl>
        <ccimDesc>충주 탑평리 칠층석탑 측면전경</ccimDesc>
        <sn>2</sn>
        <imageNuri>A</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612145.jpg</imageUrl>
        <ccimDesc>중원 탑평리 칠층석탑 기단부</ccimDesc>
        <sn>3</sn>
        <imageNuri>D</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612146.jpg</imageUrl>
        <ccimDesc>충주 탑평리 칠층석탑 전경</ccimDesc>
        <sn>4</sn>
        <imageNuri>A</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612147.jpg</imageUrl>
        <ccimDesc>중원 탑평리 칠층석탑 탑신부</ccimDesc>
        <sn>5</sn>
        <imageNuri>A</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612148.jpg</imageUrl>
        <ccimDesc>충주 탑평리 칠층석탑</ccimDesc>
        <sn>6</sn>
        <imageNuri>A</imageNuri>
        <imageUrl>http://www.cha.go.kr/unisearch/images/national_treasure/1612149.jpg</imageUrl>
        <ccimDesc>상륜부앙화</ccimDesc>
    </item>
</result>'''

# XML 파싱
root = ET.fromstring(xml_data)

# 결과를 저장할 딕셔너리
result = {
    "totalCnt": root.find('totalCnt').text,
    "ccbaKdcd": root.find('ccbaKdcd').text,
    "ccbaAsno": root.find('ccbaAsno').text,
    "ccbaCtcd": root.find('ccbaCtcd').text,
    "ccbaMnm1": root.find('ccbaMnm1').text.strip(),
    "ccbaMnm2": root.find('ccbaMnm2').text.strip(),
    "data": []
}

# 중복된 항목을 저장할 딕셔너리
items_dict = defaultdict(list)

# XML에서 아이템 추출
for item in root.findall('item'):
    sn = item.find('sn').text
    imageNuri = item.find('imageNuri').text
    imageUrl = item.find('imageUrl').text
    ccimDesc = item.find('ccimDesc').text

    # 중복된 항목을 그룹화
    items_dict[sn].append({
        "imageNuri": imageNuri,
        "imageUrl": imageUrl,
        "ccimDesc": ccimDesc
    })

# 데이터를 리스트로 변환
for sn, images in items_dict.items():
    result["data"].append({
        "sn": sn,
        "images": images
    })

# JSON 변환 및 출력
json_result = json.dumps(result, ensure_ascii=False, indent=4)
print(json_result)

# import xml.etree.ElementTree as ET
# import json

# # Input XML string
# xml_data = '''<?xml version="1.0" encoding="utf-8"?>
# <result>
#     <totalCnt>14</totalCnt>
#     <pageUnit>300</pageUnit>
#     <pageIndex>1</pageIndex>
#     <item>
#         <sn>1</sn>
#         <no>238</no>
#         <ccmaName><![CDATA[국보]]></ccmaName>
#         <crltsnoNm>5</crltsnoNm>
#         <ccbaMnm1><![CDATA[보은 법주사 쌍사자 석등]]></ccbaMnm1>
#         <ccbaMnm2><![CDATA[報恩 法住寺 雙獅子 石燈]]></ccbaMnm2>
#         <ccbaCtcdNm><![CDATA[충북]]></ccbaCtcdNm>
#         <ccsiName><![CDATA[보은군]]></ccsiName>
#         <ccbaAdmin><![CDATA[법주사]]></ccbaAdmin>
#         <ccbaKdcd>11</ccbaKdcd>
#         <ccbaCtcd>33</ccbaCtcd>
#         <ccbaAsno>00050000</ccbaAsno>
#         <ccbaCncl>N</ccbaCncl>
#         <ccbaCpno>1113300050000</ccbaCpno>
#         <longitude>127.833219375596</longitude>
#         <latitude>36.5421679403972</latitude>
#         <regDt>2024-01-25 14:25:02</regDt>
#     </item>
# </result>'''

# # Parse the XML
# root = ET.fromstring(xml_data)

# # Helper function to remove CDATA and unwanted characters from text
# def clean_text(text):
#     if text:
#         return text.replace('<![CDATA[', '').replace(']]>', '').replace('<', '').replace('>', '').replace('!', '').replace('[', '').replace(']', '')
#     return text

# # Convert XML to dictionary
# def xml_to_dict(element):
#     if len(element) == 0:
#         return clean_text(element.text)
#     return {child.tag: xml_to_dict(child) for child in element}

# # Convert the root element to a dictionary
# data_dict = xml_to_dict(root)

# # Convert dictionary to JSON
# json_data = json.dumps(data_dict, ensure_ascii=False, indent=4)

# # Print the JSON data
# print(json_data)
