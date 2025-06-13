FROM ccr.ccs.tencentyun.com/python-custom/python:web-1.0

# 设置时区环境变量
ENV TZ=Asia/Shanghai

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY . /app

# 安装 Python 依赖
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple/

# 暴露端口
EXPOSE 8769

# 使用 supervisor 启动服务
CMD ["/usr/bin/supervisord", "-n", "-c", "supervisord.conf"]