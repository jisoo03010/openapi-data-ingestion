import pymysql
import configparser
import pandas as pd

# Config 파일 읽기
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

# 데이터베이스 연결 함수

# 데이터베이스에 데이터 삽입
def insert_data(df, conn):
    cursor = conn.cursor()

    # Insert query
    insert_query = """
    INSERT INTO TB_WATER_QUALITY_OBSERVATION_POINT (
        wmyr, ptNo, ptNm, addr, major_basin, sub_basin, lon, lat
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Prepare data for insertion
    values = df.to_records(index=False).tolist()

    try:
        # Insert each row
        cursor.executemany(insert_query, values)
        conn.commit()
        print("Data inserted successfully.")
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    # Excel 파일 경로
    excel_file = 'water_level.xlsx'

    # 엑셀 파일에서 데이터 읽기
    df = pd.read_excel(excel_file, sheet_name='Data')  # 시트 이름을 실제 시트 이름으로 변경

    # 데이터베이스 연결
    def db_connect():
        db_user = config.get('DATABASE', 'db_user')
        db_password = config.get('DATABASE', 'db_password')
        db_host = config.get('DATABASE', 'db_host')
        db_port = config.getint('DATABASE', 'db_port')
        db_database = config.get('DATABASE', 'db_database')

        conn = pymysql.connect(
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            database=db_database
        )
        return conn
    conn = db_connect()
    try:
        # 데이터 삽입
        insert_data(df, conn)
    finally:
        # 데이터베이스 연결 종료
        conn.close()

if __name__ == "__main__":
    main()
