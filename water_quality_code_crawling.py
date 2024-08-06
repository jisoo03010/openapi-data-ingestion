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
excel_file_path = 'water_quality_code.xlsx'

# 엑셀 파일 읽기
df = pd.read_excel(excel_file_path)

df = df.where(pd.notnull(df), None)
# 데이터프레임 컬럼 이름 확인
print("DataFrame columns:", df.columns)

# MySQL 데이터베이스 연결
connection = pymysql.connect(**db_config)
cursor = connection.cursor()


# 데이터 삽입 SQL
insert_sql = '''
INSERT INTO tb_gt_water_quality_observation_point (wmyr, ptNo, kdiNm, ptNm, addr, major_basin, sub_basin)
VALUES (%s, %s, %s, %s, %s, %s, %s)
'''

# 데이터 삽입
for _, row in df.iterrows():
    print("", row)
    data = (
        row.iloc[0],  # ktsn
        row.iloc[1],   # name
        row.iloc[2],  # imgUrl
        row.iloc[3],  # imgUrl
        row.iloc[4],  # imgUrl
        row.iloc[5],  # imgUrl
        row.iloc[6],  # imgUrl
    )
    cursor.execute(insert_sql, data)

# 커밋 및 연결 종료
connection.commit()
cursor.close()
connection.close()

print("Data successfully inserted into the database.")
