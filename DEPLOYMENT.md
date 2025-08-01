# TimeHacker API 服务器部署操作流程

## 域名架构说明

本项目采用子域名架构：

- **前端应用**: `https://my-domain.com` 和 `https://www.my-domain.com`
- **API 服务**: `https://api.my-domain.com`

这种架构的优势：

- 清晰的服务分离
- 便于负载均衡和扩展
- 支持独立的 SSL 证书管理
- 更好的缓存策略

## 前期准备

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **内存**: 最少 2GB RAM (推荐 4GB)
- **存储**: 最少 20GB SSD
- **网络**: 公网 IP，开放端口 80, 443, 22

### 2. 域名配置

设置以下 DNS 记录：

```
# A记录
my-domain.com           A    your-server-ip
www.my-domain.com       A    your-server-ip
api.my-domain.com       A    your-server-ip

# 或使用CNAME（如果主域名已设置A记录）
www                     CNAME my-domain.com
api                     CNAME my-domain.com
```

等待 DNS 解析生效 (通常 5-30 分钟)

## 服务器初始化

### 1. 连接服务器

```bash
ssh root@your-server-ip
```

### 2. 更新系统

```bash
apt update && apt upgrade -y
apt install -y curl wget git ufw
```

### 3. 配置防火墙

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 4. 创建部署用户

```bash
adduser deployer
usermod -aG sudo deployer
su - deployer
```

## 安装 Docker 和 Docker Compose

### 1. 安装 Docker

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

### 2. 安装 Docker Compose

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. 验证安装

```bash
docker --version
docker-compose --version
```

## 代码部署

### 1. 克隆代码仓库

```bash
cd /home/deployer
git clone https://github.com/YourUsername/timehacker-api.git
cd timehacker-api/backend
```

### 2. 配置环境变量

```bash
cp .env.example .env
nano .env
```

**编辑 .env 文件，配置以下变量：**

```env
# 应用配置
ENVIRONMENT=production
DEBUG=false

# Supabase配置（从你的Supabase控制台获取）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# 安全配置
SECRET_KEY=your_very_secure_secret_key_here_use_random_64_chars

# 域名配置
API_DOMAIN=api.my-domain.com
FRONTEND_DOMAIN=my-domain.com
ALLOWED_ORIGINS=https://my-domain.com,https://www.my-domain.com

# CORS配置
CORS_ALLOWED_ORIGINS=["https://my-domain.com", "https://www.my-domain.com"]
```

### 3. 配置 Nginx

```bash
nano nginx.conf
```

**替换域名：**

- 将配置文件中的 `api.my-domain.com` 替换为你的实际 API 域名
- 确保 server_name 正确配置为你的 API 子域名

## SSL 证书配置

### 1. 安装 Certbot

```bash
sudo apt install -y certbot
```

### 2. 停止可能占用 80 端口的服务

```bash
sudo systemctl stop apache2 nginx || true
```

### 3. 获取 SSL 证书

```bash
sudo certbot certonly --standalone -d api.my-domain.com
```

### 4. 创建 SSL 目录并复制证书

```bash
mkdir -p ssl
sudo cp /etc/letsencrypt/live/api.my-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/api.my-domain.com/privkey.pem ssl/key.pem
sudo chown -R deployer:deployer ssl/
```

## 应用部署

### 1. 构建和启动服务

```bash
chmod +x scripts/*.sh
sudo ./scripts/deploy.sh
```

### 2. 检查服务状态

```bash
docker-compose ps
docker-compose logs api
docker-compose logs nginx
```

### 3. 测试 API

```bash
curl https://api.my-domain.com/health
curl https://api.my-domain.com/docs
```

## 设置自动证书续期

### 1. 创建续期脚本

```bash
sudo nano /usr/local/bin/renew-certs.sh
```

**添加以下内容：**

```bash
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/api.my-domain.com/fullchain.pem /home/deployer/timehacker-api/backend/ssl/cert.pem
cp /etc/letsencrypt/live/api.my-domain.com/privkey.pem /home/deployer/timehacker-api/backend/ssl/key.pem
chown deployer:deployer /home/deployer/timehacker-api/backend/ssl/*
cd /home/deployer/timehacker-api/backend && docker-compose restart nginx
```

### 2. 设置执行权限和定时任务

```bash
sudo chmod +x /usr/local/bin/renew-certs.sh
sudo crontab -e
```

**添加以下行（每天凌晨 2 点检查证书）：**

```
0 2 * * * /usr/local/bin/renew-certs.sh
```

## 监控和日志

### 1. 查看日志

```bash
# 查看应用日志
docker-compose logs -f api

# 查看Nginx日志
docker-compose logs -f nginx

# 查看系统资源
docker stats
```

### 2. 设置日志轮转

```bash
sudo nano /etc/logrotate.d/docker-compose
```

**添加以下内容：**

```
/home/deployer/timehacker-api/backend/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    notifempty
    create 644 deployer deployer
    postrotate
        docker-compose -f /home/deployer/timehacker-api/backend/docker-compose.yml restart nginx
    endscript
}
```

## 应用更新流程

### 1. 创建更新脚本

```bash
nano scripts/update.sh
```

**添加以下内容：**

```bash
#!/bin/bash
echo "🔄 Updating TimeHacker API..."

# 备份当前版本
git stash
git pull origin main

# 重新构建和部署
docker-compose build --no-cache
docker-compose up -d

echo "✅ Update completed!"
```

### 2. 使用更新脚本

```bash
chmod +x scripts/update.sh
./scripts/update.sh
```

## 性能优化

### 1. 设置 Swap（如果内存小于 4GB）

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 2. Docker 容器资源限制

编辑 `docker-compose.yml`，添加资源限制：

```yaml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
        reservations:
          memory: 512M
```

## 安全加固

### 1. 更改 SSH 端口（可选）

```bash
sudo nano /etc/ssh/sshd_config
# 修改 Port 22 为其他端口，如 Port 2222
sudo systemctl restart ssh
# 记得在防火墙中开放新端口
sudo ufw allow 2222/tcp
```

### 2. 设置 fail2ban 防护

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## 备份策略

### 1. 创建备份脚本

```bash
nano scripts/backup.sh
```

**添加以下内容：**

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/deployer/backups"
mkdir -p $BACKUP_DIR

# 备份代码
tar -czf $BACKUP_DIR/code_$DATE.tar.gz /home/deployer/timehacker-api

# 备份Docker volumes（如果有）
docker-compose down
tar -czf $BACKUP_DIR/volumes_$DATE.tar.gz /var/lib/docker/volumes
docker-compose up -d

# 清理旧备份（保留30天）
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR"
```

### 2. 设置定时备份

```bash
chmod +x scripts/backup.sh
crontab -e
```

**添加以下行（每天凌晨 3 点备份）：**

```
0 3 * * * /home/deployer/timehacker-api/backend/scripts/backup.sh
```

## 故障排查

### 1. 常见问题检查清单

- [ ] 检查 DNS 解析：`nslookup api.my-domain.com`
- [ ] 检查端口开放：`sudo netstat -tlnp | grep :80`
- [ ] 检查 SSL 证书：`openssl s_client -connect api.my-domain.com:443`
- [ ] 检查 Docker 服务：`docker-compose ps`
- [ ] 检查应用日志：`docker-compose logs api`

### 2. 紧急回滚

```bash
# 停止服务
docker-compose down

# 回滚到上一个版本
git log --oneline -5  # 查看最近的提交
git checkout <previous-commit-hash>

# 重新部署
docker-compose up -d
```

## 完成部署

部署完成后，你的 API 将在以下地址可用：

- **API 服务**: https://api.my-domain.com
- **API 文档**: https://api.my-domain.com/docs
- **健康检查**: https://api.my-domain.com/health
- **前端应用**: https://my-domain.com (需要单独部署前端项目)

记住定期：

1. 检查服务状态
2. 更新系统和依赖
3. 监控资源使用
4. 验证备份完整性

## 前端部署建议

虽然本文档主要关注 API 部署，但为了完整的系统架构，建议：

1. **前端静态文件**: 可以使用 Nginx 托管，或部署到 CDN
2. **前端域名**: 配置 `my-domain.com` 和 `www.my-domain.com` 指向前端应用
3. **CORS 配置**: 确保 API 的 CORS 设置允许前端域名访问
4. **SSL 证书**: 为前端域名也配置 SSL 证书
