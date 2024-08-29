import pymysql
import configparser as parser 
import configparser
import datetime
import pandas as pd
import math
# import logging
# logger = logging.getLogger(__name__)
# logging.basicConfig(filename='data.log', encoding='utf-8', level=logging.DEBUG)


    
config = configparser.RawConfigParser()
config.read("config.ini", encoding="utf-8")

    
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

    cursor = conn.cursor()
    return  cursor, conn

def db_pk_delete(table_name):
    cursor, conn = db_connect()
    select_query = f"select EXISTS (select * from {table_name} limit 1) as success"
    cursor.execute(select_query) 
    result = cursor.fetchone()
    
    # 만약 실시간으로 가져오는 데이터가 아닌 데이터를 주욱 가져오는 API 는 
    if result[0] == 1: 
        delete_query = f"delete from {table_name}"
        # print("이미 데이터가 존재함으로 데이터를 모두 삭제합니다.")
        cursor.execute(delete_query) 
    conn.commit()

def save_to_database(table_name, columns_str, data_frame):
    cursor, conn = db_connect()
    db_pk_delete(table_name)
    # v
    try:
        data_frame = data_frame.where(pd.notnull(data_frame), '')
        columns = data_frame.columns.tolist()
        
        if table_name == 'tb_gt_water_quality':
            columns.remove('ROWNO')
        elif table_name == 'tb_gt_water_level' or table_name == 'tb_gt_water_level_observation_point' or table_name == 'tb_gt_rainfall' or table_name == 'tb_gt_rainfall_observation_point':
            columns.remove('links')
        elif table_name == 'tb_gt_cultural':
            columns.remove('sn')
            columns.remove('crltsnoNm')
        elif table_name == 'tb_gt_cultural_img':
            columns.remove('sn')
            
            
        for _, row in data_frame.iterrows():
            values = tuple(None if isinstance(row[col], float) and math.isnan(row[col]) else row[col] for col in columns)

            
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES {values}"
             # db 저장 메서드
            # print("\n\n\n\n\nQuery ------------------------------\n", insert_query)
            cursor.execute(insert_query)
            
        conn.commit()
        print("성공적으로 데이터가 삽입되었습니다!")
        
    except pymysql.e as e :
        print(f"Error inserting data: {e}")
        conn.rollback()
    finally:
        conn.close()