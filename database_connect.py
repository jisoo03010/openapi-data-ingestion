import pymysql
import configparser as parser 
import configparser
import datetime
import pandas as pd
import math
    
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

def save_to_database(table_name, columns_str, data_frame):
    cursor, conn = db_connect()
    # v
    try:
        data_frame = data_frame.where(pd.notnull(data_frame), '')

        columns = data_frame.columns.tolist()
        if 'ROWNO' in columns:
            columns.remove('ROWNO')
        for _, row in data_frame.iterrows():
            values = tuple(None if isinstance(row[col], float) and math.isnan(row[col]) else row[col] for col in columns)
            values += (datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            insert_query = f"INSERT INTO {table_name} ({columns_str}) VALUES {values}"
            print("\n\n\n\n\nQuery ------------------------------\n", insert_query)
            cursor.execute(insert_query)
        conn.commit()
        print("성공적으로 데이터가 삽입되었습니다!")
        
    except pymysql.Error as e:
        print(f"Error inserting data: {e}")
        conn.rollback()
    
    finally:
        conn.close()