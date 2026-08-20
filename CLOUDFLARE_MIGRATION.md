# ============================================================
# Cloudflare Pages 部署指南
# 目标：把雷达站从 GitHub Pages 迁移到 Cloudflare Pages
# 好处：国内访问更稳定 + 缓存问题根治（_headers 已配置不缓存）
# 注意：需要 Cloudflare 账号（免费），这一步必须你本人在场
# ============================================================

## 为什么迁移
1. GitHub Pages 国内访问不稳定（偶发白屏/加载失败）
2. 手机缓存旧内容的问题（Cloudflare 用 _headers 根治）
3. Cloudflare 免费版无流量限制，且自带 CDN 加速

## 准备工作（我已全部做好）
- ✅ `_headers` 文件（配置所有页面不缓存）
- ✅ `wrangler` 已安装（Cloudflare 官方 CLI）
- ✅ 云端代码已就绪（app.html / version.txt / 自动构建逻辑）

---

## 你回来只需要做 3 步（每步 2-3 分钟）

### 第 1 步：注册/登录 Cloudflare（免费）
打开浏览器：https://dash.cloudflare.com/sign-up
- 用邮箱注册（或已有账号直接登录）
- 不需要绑定信用卡

### 第 2 步：登录 wrangler（命令行授权）
打开 Mac「终端」，运行：
```bash
wrangler login
```
- 会自动打开浏览器 → 点 Allow（授权）
- 授权成功终端会显示 "Successfully logged in"

### 第 3 步：告诉我"已登录"
回到和我的对话，说一声"登录好了"
→ 剩下的我全部接手：
   - 创建 Pages 项目
   - 上传部署（用 wrangler pages deploy）
   - 验证线上访问
   - 给你新的访问地址

---

## 部署后的变化
| 项目 | 之前（GitHub Pages） | 之后（Cloudflare Pages） |
|------|-------------------|------------------------|
| 访问地址 | tkdzqc33-pixel.github.io/radar-station/ | **xxx.pages.dev/radar-station/**（新地址） |
| 国内访问 | 时快时慢 | 更稳定 |
| 缓存问题 | 手机缓存旧内容 | _headers 根治，永不缓存 |
| 自动更新 | GitHub Actions | 仍由 GitHub Actions 生成数据，Cloudflare 拉取部署（或手动上传） |

## 注意
- 迁移后**旧地址还能用**（GitHub Pages 保留），新地址是 Cloudflare 的
- 以后手机用新地址，把新地址添加到主屏幕
- 数据仍由 GitHub Actions 每天自动生成（不变），只是托管换到 Cloudflare
