import os
import glob
import mysql.connector
from mysql.connector import Error
from flask import jsonify
from dotenv import load_dotenv
import os
import sys

from application.config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME, DOMAIN


# 连接到MySQL数据库
def create_connection():
    connection = None
    if os.getenv('DATABASE') == 'ON':
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
    return connection

# 插入数据到plist表格
def insert_plist_data(plist_filename, url, filename):
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                insert_query = """
                INSERT INTO plist (plist_filename, url, filename)
                VALUES (%s, %s, %s)
                """
                data = (plist_filename, url, filename)
                cursor.execute(insert_query, data)
                connection.commit()
                print("Data inserted into plist table")
            except Error as e:
                print(f"Error inserting data into plist table: {e}")
            finally:
                cursor.close()
                connection.close()

# 获取数据库中的所有记录
def get_all_records():
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                select_query = "SELECT plist_filename, url, filename FROM plist"
                cursor.execute(select_query)
                results = cursor.fetchall()
                return results
            except Error as e:
                print(f"Error retrieving data from plist table: {e}")
            finally:
                cursor.close()
                connection.close()
    return []


# 检查本地.plist文件是否在数据库中有记录，如果没有则插入记录

def check_local_files(plist_folder, results):
    generated_count = 0
    inserted_count = 0

    for plist_file in glob.glob(os.path.join(plist_folder, '*.plist')):
        plist_filename = os.path.basename(plist_file)
        plist_code = plist_filename[:-6] if plist_filename.endswith('.plist') else ''
        plist_filepath = os.path.join('plist', plist_filename)

        found = False
        for result in results:
            if plist_filename == result[0]:
                found = True
                break
        if not found:
            with open(plist_filepath, 'r') as plist_file:
                plist_content = plist_file.read()

            title_start_index = plist_content.find('<key>title</key>') + len('<key>title</key>') + 7
            title_end_index = plist_content.find('</string>', title_start_index)
            title = plist_content[title_start_index:title_end_index].strip().strip('<string>')



            if len(title) > 61:
                title = title[:40] + '..'

            url_start_index = plist_content.find('<key>url</key>') + len('<key>url</key>') + 7
            url_end_index = plist_content.find('</string>', url_start_index)
            url = plist_content[url_start_index:url_end_index].strip().strip('<string>')

            # 替换 <string> 标签
            title = title.replace('<string>', '')
            title = title.replace('              ', '')
            url = url.replace('<string>', '')

            # 插入数据到数据库
            insert_plist_data(plist_filename, url, title)
#            generated_count += 1
            inserted_count += 1

    return {'status': 'success', 'generated_count': generated_count, 'inserted_count': inserted_count}


# 检查数据库中的记录是否在本地.plist文件中有对应文件，如果没有则生成对应的.plist文件
def check_database_records(plist_folder, results):
    generated_count = 0
    inserted_count = 0
    for result in results:
        plist_filename = result[0]
        plist_filepath = os.path.join(plist_folder, plist_filename)

        if not os.path.exists(plist_filepath):
            url = result[1]
            filename = result[2]

            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>items</key>
                <array>
                    <dict>
                        <key>assets</key>
                        <array>
                            <dict>
                                <key>kind</key>
                                <string>software-package</string>
                                <key>url</key>
                                <string>{url}</string>
                            </dict>
                            <dict>
                                <key>kind</key>
                                <string>display-image</string>
                                <key>url</key>
                                <string>{DOMAIN}/static/logo.png</string>
                            </dict>
                        </array>
                        <key>metadata</key>
                        <dict>
                            <key>bundle-identifier</key>
                            <string>*</string>
                            <key>bundle-version</key>
                            <string>1.0</string>
                            <key>kind</key>
                            <string>software</string>
                            <key>title</key>
                            <string>{filename}</string>
                        </dict>
                    </dict>
                </array>
            </dict>
            </plist>'''

            with open(plist_filepath, 'w') as plist_file:
                plist_file.write(plist_content)
            generated_count += 1
    return {'status': 'success', 'generated_count': generated_count, 'inserted_count': inserted_count}
def sync():
    plist_folder = os.path.join(os.path.dirname(__file__), '../', 'plist')
    results = get_all_records()

    generated_count = 0
    inserted_count = 0

    generated_inserted_counts = check_local_files(plist_folder, results)
    generated_count += generated_inserted_counts['generated_count']
    inserted_count += generated_inserted_counts['inserted_count']

    check_database_records(plist_folder, results)

    return {'status': 'success', 'generated_count': generated_count, 'inserted_count': inserted_count}
