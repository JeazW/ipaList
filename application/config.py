import os
from dotenv import load_dotenv
# 加载.env文件中的变量
load_dotenv()

# 获取页数设置
per_page = int(os.getenv('PERPAGE', '10'))
NOTICE = os.getenv('NOTICE', 'ON')
# 从环境变量或者.env文件中获取URL变量
DOMAIN = os.getenv('DOMAIN')
# 从环境变量或者.env文件中获取敏感信息变量
SECRET_KEY = os.getenv('SALT', 'your_secret_salt')
USERNAME = os.getenv('USERNAME', 'admin')
PASSWORD = os.getenv('PASSWORD', '123456')
DATABASE = os.getenv('DATABASE', 'OFF')

# 从环境变量或者.env文件中获取数据库信息
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '18102')
DB_USER = os.getenv('DB_USER', 'plistuser')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'plist123.')
DB_NAME = os.getenv('DB_NAME', 'plist_db')

