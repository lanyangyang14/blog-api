# ============ 阶段 1：构建 Vue 前端 ============
FROM node:20-alpine AS builder

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY package*.json ./
RUN npm install

# 复制代码并打包
COPY . .
RUN npm run build

# ============ 阶段 2：Nginx 运行环境 ============
FROM nginx:alpine

COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
