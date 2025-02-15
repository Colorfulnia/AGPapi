# 使用官方的轻量级 Python 3.10-slim 镜像
FROM python:3.10-slim

# 安装系统依赖（这些依赖是 Playwright 和 Chromium 需要的）
RUN apt-get update && apt-get install -y \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libdrm-dev \
    libx11-xcb1 \
    libxcomposite-dev \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libcairo2 \
    libnss3 \
    libgtk-3-0 \
    libxss1 \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制 requirements.txt 并安装 Python 依赖
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 安装 Playwright 并安装所需的 Chromium 浏览器（--with-deps 安装必要的系统依赖）
RUN pip install playwright && playwright install --with-deps chromium

# 复制项目所有文件到容器中
COPY . /app

# 暴露 Flask 默认端口
EXPOSE 5000

# 指定容器启动命令
CMD ["python", "app.py"]