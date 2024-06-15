# ipaList

> 这个小项目是用来根据ipa直链生成plist文件后以应用列表的形式管理起来，旨在方便苹果老设备尤其是IOS6系统在线安装越狱应用。
可以配合目录程序管理老ios越狱应用ipa包，比如Alist程序（Alist本身支持在线安装，可惜老系统的浏览器不兼容）

> 声明：找了一大圈没找到类似的项目，决定自己做个有些基本功能的简单页面。本人不会开发语言，项目代码全由ChatGPT生成。所以结构和样式、功能有些简陋，如果有人提ISSUE我恐怕解决起来也比较困难。

## TodoList
- [ ]加个API接口用来批量生成数据
- [x]自定义文件名称
- [ ]deb源的支持
- [x]公告功能
- [ ]密码加密
- [ ]无数据库时启动校验
- [x]批量新增等待条
- [x]plist文件与数据库同步
- [x]去重
- [ ]plist路径rewrite
- [x]删除提醒
- [x]批量新增100限制
- [x]页数跳转
- [ ]公告只在第一页
## 效果图

### **手机端（iphone4s-ios6.1.3）**
<div style="display: flex;">
  <div style="flex: 50%; padding: 5px;">
    <img src="https://github.com/JeazW/ipaList/assets/75829171/9386e868-624c-404e-bb22-ec1eac53a220" alt="手机端游客页" style="width: 30%;">
  </div>
  <div style="flex: 50%; padding: 5px;">
    <img src="https://github.com/JeazW/ipaList/assets/75829171/742a28d5-b9f1-47a3-971f-8c120d60dd1c" alt="手机端管理页" style="width: 30%;">
  </div>
</div>

### **电脑端游客页**

![](https://github.com/JeazW/ipaList/assets/75829171/428d9fee-ee8e-4405-a3c5-c8f20b9d8e63)
### **电脑端管理页**

![](https://github.com/JeazW/ipaList/assets/75829171/fd95f9dc-5197-4ad0-9f46-827f1959a0ee)

## 源码部署方法：

**环境：python3.8或以上**

```bash
git clone https://github.com/JeazW/ipaList.git
cd ipaList
pip install -r requirements.txt
#或者采用或内加速源：
pip install -r -i https://mirrors.aliyun.com/pypi/simple/ requirements.txt
```
### **在`.env`文件内配置环境变量**
**编辑文件**
```bash
vim .env
```
**写入配置**：
```
#域名（必填）
DOMAIN=https://example.xom
#管理用户名（默认admin）
USERNAME=admin
#管理密码（默认123456）
PASSWORD=123456
#每页数量
PERPAGE=100
```
> 注意运行前把变量替换成自己的
```bash
python app.py
```

# Docker部署方法
### 拉取镜像：
```bash
docker pull jeazw92/ipalist:latest
```
### 运行容器：
```bash
docker run -itd --name ipaList -e DOMAIN=https://example.com -e USERNAME=admin -e PASSWORD=123456 -p 8084:5000 jeazw92/ipalist:latest
```
如果需要手动管理生成的plist文件，则可以将plist目录映射出来：
```bash
docker run -itd --name ipaList -e DOMAIN=https://example.com -e USERNAME=admin -e PASSWORD=123456 -v /data/docker/ipaList:/app/plist -p 8084:5000 jeazw92/ipalist:latest
```
> 注意运行前把变量替换成自己的
# docker-compose部署方法：
```
mkdir ipaList
cd ipaList
```
### **创建docker-compose.yml**
```bash
vim docker-compose.yml
```

```bash
version: '3'

services:
  ipalist:
    # 使用镜像 "jeazw92/ipalist:latest"
    image: jeazw92/ipalist:latest

    # 将容器的 5000 端口映射到主机的 8084 端口
    ports:
      - 8084:5000

    # 设置容器的环境变量
    environment:
      - DOMAIN=https://example.com
      - USERNAME=admin
      - PASSWORD=123456

    # 将主机的 "/data/docker/plist" 目录挂载到容器的 "/app/plist" 目录
    # 此项可选，不需要可以删除
    volumes:
      - /data/docker/ipalist:/app/plist
```
> 注意运行前把变量替换成自己的
### 运行容器
```bash
docker-compose up -d
```

# 使用方法
点击“新增”，把ipa链接（直链）填入即可
