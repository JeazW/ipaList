# 使用Alpine作为基础镜像
FROM python:3.8.3-alpine

# 设置工作目录
WORKDIR /app

# 将当前目录下的所有文件复制到镜像的/app目录下
COPY . /app

# 更换 pip 源为阿里云镜像 1
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 暴露应用程序的端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=app.py

# 运行应用程序
CMD ["flask", "run", "--host=0.0.0.0"]
