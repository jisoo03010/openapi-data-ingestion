import pandas as pd
import pymysql

# MySQL 데이터베이스 연결 설정
db_config = {
    'host': '172.17.252.108',
    'port': 3306,
    'user': 'root',
    'password': 'eoqkrWkd!@3',
    'database': 'whaleshark_lite2'
}

# 엑셀 파일 경로
excel_file_path = 'lon_lat_info.xlsx'

# 엑셀 파일 읽기
df = pd.read_excel(excel_file_path, skiprows=1)

# NaN 값을 None으로 변환
df = df.applymap(lambda x: None if pd.isna(x) else x)

print(df.head())  # 변환된 데이터 프레임의 첫 몇 줄을 출력해 확인

# 데이터프레임 컬럼 이름 확인
print("DataFrame columns:", df.columns)

# MySQL 데이터베이스 연결
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# 데이터 삽입 SQL
insert_sql = '''
INSERT INTO tb_gt_coordinates (sort, locCode, step1, step2, step3, gridX, gridY, lonHour, lonMinute, lonSecond, latCity, latMinute, latSecond, second100, latSecond100, updateLoc)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
'''

# 데이터 삽입
for _, row in df.iterrows():
    # 데이터 튜플 생성 및 NaN -> None 변환
    data = tuple(None if pd.isna(x) else x for x in row[:16])
    
    # 데이터 출력
    print("data : ", data)
    
    # SQL 쿼리 실행
    cursor.execute(insert_sql, data)

# 커밋 및 연결 종료
conn.commit()
cursor.close()
conn.close()

print("Data successfully inserted into the database.")
