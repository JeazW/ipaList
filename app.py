import os
import random
import string
import glob
import urllib
from urllib.parse import quote, unquote
from math import ceil
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, abort, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from dotenv import load_dotenv
import flask
import mysql.connector
from mysql.connector import Error
import logging

from application.sync import sync

from application.config import per_page, NOTICE, DOMAIN, SECRET_KEY, USERNAME, PASSWORD, DATABASE, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

# 打印变量值
print(f"分页: {per_page}")
print(f"公告开关: {NOTICE}")
print(f"域名: {DOMAIN}")
print(f"密码盐: {SECRET_KEY}")
print(f"用户名: {USERNAME}")
print(f"密码: {PASSWORD}")
print(f"数据库开关: {DATABASE}")
print(f"数据库主机: {DB_HOST}")
print(f"数据库端口: {DB_PORT}")
print(f"数据库用户: {DB_USER}")
print(f"数据库密码: {DB_PASSWORD}")
print(f"数据库名: {DB_NAME}")

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3600  # 设置静态文件缓存时间（单位：秒）
app.config['SECRET_KEY'] = SECRET_KEY   # 设置一个密钥，用于加密用户凭证

login_manager = LoginManager()
login_manager.init_app(app)

# 定义用户模型
class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

# 模拟一个用户数据库
users = {
    USERNAME: User(USERNAME, PASSWORD),
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

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
#            print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL database: {e}")
    return connection

# 创建plist表格（如果不存在）
def create_plist_table():
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                create_table_query = """
                CREATE TABLE IF NOT EXISTS plist (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    plist_filename VARCHAR(255) NOT NULL,
                    url VARCHAR(1280) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_table_query)
                connection.commit()
                print("plist table created")
            except Error as e:
                print(f"Error creating plist table: {e}")
            finally:
                cursor.close()
                connection.close()

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

# 删除plist表格中的记录
def delete_plist_data(plist_filename):
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                delete_query = "DELETE FROM plist WHERE plist_filename = %s"
                data = (plist_filename,)
                cursor.execute(delete_query, data)
                connection.commit()
                print("Data deleted from plist table")
            except Error as e:
                print(f"Error deleting data from plist table: {e}")
            finally:
                cursor.close()
                connection.close()

def check_duplicate(url):
    is_duplicate = False
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                select_query = "SELECT COUNT(*) FROM plist WHERE url = %s"
                data = (url,)
                cursor.execute(select_query, data)
                result = cursor.fetchone()
                count = result[0]
                if count > 0:
                    is_duplicate = True
            except Error as e:
                print(f"Error checking duplicate in database: {e}")
            finally:
                cursor.close()
                connection.close()
    else:
        plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
        plist_files = glob.glob(os.path.join(plist_folder, '*.plist'))
        for plist_file in plist_files:
            with open(plist_file, 'r') as file:
                plist_content = file.read()
                if url in plist_content:
                    is_duplicate = True
    return is_duplicate


import locale
from math import ceil
from pypinyin import pinyin, NORMAL


# 设置本地化环境为当前系统默认
locale.setlocale(locale.LC_ALL, '')

def get_sorted_plist_files():
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_files = glob.glob(os.path.join(plist_folder, '*.plist'))
    plist_info = []

    for plist_file in plist_files:
        plist_filename = os.path.basename(plist_file)
        plist_code = plist_filename[:-6] if plist_filename.endswith('.plist') else ''
        plist_filepath = os.path.join('plist', plist_filename)

        with open(plist_filepath, 'r') as plist_file:
            plist_content = plist_file.read()

            title_start_index = plist_content.find('<key>title</key>') + len('<key>title</key>') + 7
            title_end_index = plist_content.find('</string>', title_start_index)
            title = plist_content[title_start_index:title_end_index].strip('<string>')

#            if len(title) > 61:
#                title = title[:40] + '..'

        # 将中文标题转换为拼音字符串，并按拼音排序
        pinyin_title = ''.join([p[0] for p in pinyin(title, style=NORMAL)])
        plist_info.append({'filename': plist_filename, 'code': plist_code, 'title': title, 'pinyin_title': pinyin_title})

    # 按拼音排序
    plist_info.sort(key=lambda x: x['pinyin_title'])

    return plist_info

@app.route('/')
def index():
    # 公告内容
    notice_content = ""
    if NOTICE == 'ON':
        with open('notice.txt', 'r') as file:
            notice_content = file.read()

    # 获取排序后的文件列表
    plist_info = get_sorted_plist_files()

    # 获取已收录应用的数量
    app_count = len(plist_info)

    # 分页逻辑
    page = request.args.get('page', default=1, type=int)
    total_pages = ceil(len(plist_info) / per_page)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    plist_info = plist_info[start_index:end_index]

    domain = DOMAIN  # 使用定义的URL变量
    return render_template('index.html', notice_content=notice_content, domain=domain, plist_info=plist_info, page=page, total_pages=total_pages, app_count=app_count)

def get_filename_from_url(url):
    return urllib.parse.unquote(os.path.basename(url))

def is_valid_url(url):
    return url.startswith('http://') or url.startswith('https://')

# 设置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)





@app.route('/ipa')
@login_required
def generate_plist_from_url():
    ipa_url = request.args.get('url')
    encoded_ipa_url = quote(ipa_url, safe=':/')

    filename = request.args.get('filename')

    # Check for duplicate URL
    if check_duplicate(ipa_url):
        logger.warning(f"Duplicated URL: {ipa_url}")
        return jsonify({'status': 'duplicate'})

    if not ipa_url.startswith("http") or not ipa_url.endswith(".ipa"):
        logger.warning(f"Invalid URL: {ipa_url}")
        return jsonify({'status': 'invalid'})

    random_filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
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
                        <string>{ipa_url}</string>
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
                    <string>{filename if filename else get_filename_from_url(ipa_url)}</string>
                </dict>
            </dict>
        </array>
    </dict>
    </plist>'''

    plist_filename = f'{random_filename}.plist'
    with open(f'plist/{plist_filename}', 'w') as plist_file:
        plist_file.write(plist_content)

    if not filename:
        filename = get_filename_from_url(ipa_url)

    insert_plist_data(plist_filename, ipa_url, filename)

    plist_url = f"{DOMAIN}/plist/{plist_filename}"
    return jsonify({'status': 'success', 'plist_url': plist_url})





@app.route('/plist/<filename>')
def plist(filename):
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    return send_from_directory(plist_folder, filename)

@app.route('/plist_list')
@login_required  # 添加@login_required装饰器，要求用户登录才能访问该页面
def plist_list():
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_files = glob.glob(os.path.join(plist_folder, '*.plist'))
    plist_info = []

    for index, plist_file in enumerate(plist_files):
        plist_filename = os.path.basename(plist_file)
        plist_code = plist_filename[:-6] if plist_filename.endswith('.plist') else ''
        plist_filepath = os.path.join('plist', plist_filename)

        with open(plist_filepath, 'r') as plist_file:
            plist_content = plist_file.read()

            title_start_index = plist_content.find('<key>title</key>') + len('<key>title</key>') + 7
            title_end_index = plist_content.find('</string>', title_start_index)
            title = plist_content[title_start_index:title_end_index].strip('<string>')

#            if len(title) > 60:
#                title = title[:60] + '..'

        plist_info.append({'filename': plist_filename, 'code': plist_code, 'title': title})

    # 获取排序后的文件列表
    plist_info = get_sorted_plist_files()
    # 获取已收录应用的数量
    app_count = len(plist_info)
    # 分页逻辑
    page = request.args.get('page', default=1, type=int)
#    per_page = 10
    total_pages = ceil(len(plist_info) / per_page)
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    plist_info = plist_info[start_index:end_index]

    domain = DOMAIN  # 使用定义的URL变量
    return render_template('plist_list.html', plist_info=plist_info, domain=domain, page=page, total_pages=total_pages,  database_status=DATABASE, app_count=app_count)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and user.password == password:
            login_user(user)  # 登录用户
            return redirect(url_for('plist_list'))
        else:
            return render_template('login.html', error=True)

    return render_template('login.html')


@app.route('/download_file/<filename>')
@login_required  # 添加@login_required装饰器，要求用户登录才能访问该页面
def download_file(filename):
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_filepath = os.path.join(plist_folder, filename)
    
    if os.path.exists(plist_filepath):
        with open(plist_filepath, 'r') as plist_file:
            plist_content = plist_file.read()
            url_start_index = plist_content.find('<key>url</key>') + len('<key>url</key>') + 7
            url_end_index = plist_content.find('</string>', url_start_index)
            file_url = plist_content[url_start_index:url_end_index].replace('<string>', '').strip()

            print("file_url:", file_url)  # 输出 file_url 到日志终端

            return redirect(file_url)
    else:
        return "File not found"

@app.route('/delete_plist/<filename>')
@login_required  # 添加@login_required装饰器，要求用户登录才能访问该页面
def delete_plist(filename):
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_filepath = os.path.join(plist_folder, filename)

    if os.path.exists(plist_filepath):
        os.remove(plist_filepath)
        delete_plist_data(filename)  # 删除数据库中对应的记录
        return redirect(url_for('plist_list'))
    else:
        return "File not found"

# 批量删除plist文件的路由
@app.route('/batch_delete', methods=['POST'])
@login_required  # 添加@login_required装饰器，要求用户登录才能访问该页面
def batch_delete():
    data = request.get_json()
    filenames = data.get('filenames', [])

    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    success_count = 0
    failure_count = 0

    for filename in filenames:
        plist_filepath = os.path.join(plist_folder, filename)

        if os.path.exists(plist_filepath):
            os.remove(plist_filepath)
            delete_plist_data(filename)  # 删除数据库中对应的记录
            success_count += 1
        else:
            failure_count += 1

    response = {
        'success_count': success_count,
        'failure_count': failure_count
    }

    return jsonify(response)



import logging

# 设置日志输出
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.route('/edit_plist', methods=['GET', 'POST'])
@login_required  # 添加@login_required装饰器，要求用户登录才能访问该页面
def edit_plist():
    if request.method == 'POST':
        plist_filename = request.form['plist_filename']
        url = request.form['url']
        filename = request.form['filename']

        plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
        plist_filepath = os.path.join(plist_folder, plist_filename)

        if os.path.exists(plist_filepath):
            with open(plist_filepath, 'r') as plist_file:
                plist_content = plist_file.read()

            logger.info(f"Editing plist file: url={url}, filename={filename}")

            # 在这里设置旧的链接标记字符串
            old_url = os.popen(f"grep software-package -A4 {plist_filepath} | grep url -A1 | grep url -A1|awk -F '>' 'NR==2 {{print $2}}'|awk -F '<' 'NR==1 {{print $1}}'").read().strip()
            # 在这里设置旧的文件名标记字符串
            old_filename = os.popen(f"grep -w software -A4 {plist_filepath} | grep -A1 title | grep -o '<string>[^<]*</string>' | sed 's/<[^>]*>//g'").read().strip()

            print(f"old_url: {old_url}")
            print(f"old_filename: {old_filename}")

            print(f"url: {url}")
            print(f"filename: {filename}")

            if old_url and old_filename:
                plist_content = plist_content.replace(old_url, url)
                plist_content = plist_content.replace(old_filename, filename)

                with open(plist_filepath, 'w') as plist_file:
                    plist_file.write(plist_content)

                # 更新数据库记录
                update_plist_data(plist_filename, url, filename)

                logger.info(f"Edited plist file: {plist_filename}")

                # 重新读取修改后的.plist文件内容
                with open(plist_filepath, 'r') as plist_file:
                    modified_plist_content = plist_file.read()

                logger.info(f"After editing plist file:\n{modified_plist_content}")

                return redirect(url_for('plist_list'))
            else:
                return "Replace failed"
        else:
            logger.error(f"File not found: {plist_filename}")
            return "File not found"

    plist_filename = request.args.get('filename')
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_filepath = os.path.join(plist_folder, plist_filename)

    if os.path.exists(plist_filepath):
        with open(plist_filepath, 'r') as plist_file:
            plist_content = plist_file.read()

        url_start_index = plist_content.find('<key>url</key>') + len('<key>url</key>') + 7
        url_end_index = plist_content.find('</string>', url_start_index)
        url = plist_content[url_start_index:url_end_index].replace('<string>', '').strip()

        filename_start_index = plist_content.find('<key>title</key>') + len('<key>title</key>') + 7
        filename_end_index = plist_content.find('</string>', filename_start_index)
        filename = plist_content[filename_start_index:filename_end_index].replace('<string>', '').strip()

        logger.info(f"Editing plist file: url={url}, filename={filename}")

        return render_template('edit_plist.html', plist_filename=plist_filename, url=url, filename=filename)
    else:
        logger.error(f"File not found: {plist_filename}")
        return "File not found"

def update_plist_data(plist_filename, url, filename):
    if os.getenv('DATABASE') == 'ON':
        connection = create_connection()
        if connection:
            try:
                cursor = connection.cursor()
                update_query = "UPDATE plist SET url = %s, filename = %s WHERE plist_filename = %s"
                data = (url, filename, plist_filename)
                cursor.execute(update_query, data)
                connection.commit()
                logger.info("Data updated in plist table")
            except Error as e:
                logger.error(f"Error updating data in plist table: {e}")
            finally:
                cursor.close()
                connection.close()

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '').strip()
    plist_folder = os.path.join(os.path.dirname(__file__), 'plist')
    plist_files = glob.glob(os.path.join(plist_folder, '*.plist'))
    plist_info = []

    for index, plist_file in enumerate(plist_files):
        plist_filename = os.path.basename(plist_file)
        plist_code = plist_filename[:-6] if plist_filename.endswith('.plist') else ''
        plist_filepath = os.path.join('plist', plist_filename)

        with open(plist_filepath, 'r') as plist_file:
            plist_content = plist_file.read()

            title_start_index = plist_content.find('<key>title</key>') + len('<key>title</key>') + 7
            title_end_index = plist_content.find('</string>', title_start_index)
            title = plist_content[title_start_index:title_end_index].strip('<string>')

            # 替换 <string> 标签
            title = title.replace('<string>', '')
            title = title.replace('              ', '')

#            if len(title) > 61:
#                title = title[40] + '..'

            if keyword.upper() in title.upper():  # 匹配标题
                domain = DOMAIN
                plist_info.append({'domain': domain, 'filename': plist_filename, 'code': plist_code, 'title': title})
      
    logging.info("Search results for keyword '{}': {}".format(keyword, plist_info))
    return jsonify(plist_info)

@app.route('/sync', methods=['GET'])
@login_required
def sync_route():
    result = sync()
    generated_count = result['generated_count']
    inserted_count = result['inserted_count']
    return f'Sync completed. Generated: {generated_count} .plist files, Inserted: {inserted_count} records.'



@app.route('/logout')
@login_required  # 要求用户登录才能注销
def logout():
    logout_user()  # 注销用户
    return redirect(url_for('index'))

if __name__ == '__main__':
    # 创建plist表格（如果不存在）
    create_plist_table()
    app.run(host='0.0.0.0', port=8084, debug=False)
