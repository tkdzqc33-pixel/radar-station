# 🌐 情报雷达站 · 云端部署教程（10 分钟，0 元）

把你的雷达站部署到 GitHub 免费云端，**Mac 关机也能用，手机在外面随时打开**。

---

## 一、部署后的效果

```
你的 Mac（不用开着）
    ↓
GitHub 云端（免费）每天 08:00 自动：
    ├─ 抓取新闻 + AI 分析（DeepSeek）
    ├─ 生成看板数据 + 语音简报（晓晓）
    └─ 部署到 GitHub Pages（24小时在线）
手机随时随地打开: https://你的用户名.github.io/radar-station/
```

---

## 二、操作步骤（一次搞定）

### 第 1 步：新建 GitHub 仓库（2 分钟）
1. 打开 https://github.com/new 登录你的账号
2. **Repository name** 填：`radar-station`
3. 选 **Private**（私有，别人看不到你的数据和 API key）
4. 其他默认，点 **Create repository**（创建仓库）
5. 创建后进入仓库页面，复制地址栏里的仓库地址（形如 `https://github.com/你的名字/radar-station.git`）

### 第 2 步：上传代码（2 分钟）
打开电脑「终端」，粘贴运行（把 `你的仓库地址` 换成上面复制的）：

```bash
cd /Users/a1234/Documents/DSH_Workspace/radar_station/cloud_site
git init
git add .
git commit -m "init radar"
git branch -M main
git remote add origin 你的仓库地址
git push -u origin main
```

> 如果提示登录，按提示在浏览器里完成 GitHub 登录授权。

### 第 3 步：配置密钥（2 分钟）
1. 打开你的仓库页面 → 点 **Settings**（设置）
2. 左侧菜单 → **Secrets and variables** → **Actions**
3. 点 **New repository secret**，添加两个：
   - 第一个：
     - Name: `DEEPSEEK_API_KEY`
     - Secret: 你的 DeepSeek API Key（`sk-xxxx...`）
   - 第二个（可选，要飞书推送就填）：
     - Name: `FEISHU_WEBHOOK`
     - Secret: 你的飞书机器人 webhook 地址

### 第 4 步：开启 GitHub Pages（1 分钟）
1. 仓库页面 → **Settings** → 左侧 **Pages**
2. **Source** 选 **GitHub Actions**
3. 完成（不用点别的）

### 第 5 步：手动触发第一次构建（1 分钟）
1. 仓库页面 → 点顶部 **Actions** 标签
2. 左侧选 **Radar Build & Deploy**
3. 右侧点 **Run workflow** → 绿色按钮确认
4. 等 2-3 分钟，看到绿色 ✓ 就是成功了

### 第 6 步：手机打开（完成！）
1. 仓库页面 → **Settings** → **Pages** → 顶部显示你的网址，形如：
   `https://你的用户名.github.io/radar-station/`
2. **手机浏览器**打开这个网址（任何网络都可以！）
3. **添加到主屏幕**：
   - iPhone：Safari → 分享 → 添加到主屏幕
   - 安卓：Chrome → 菜单 → 添加到主屏幕 / 安装应用
4. 完成！手机主屏幕出现「📡 雷达站」图标，点开就是全屏 App

---

## 三、之后每天自动运行

部署好就不需要再管了：
- **每天 08:00**（北京时间）自动抓取分析、更新看板
- **每周日 09:00** 自动跑一次周报数据
- 想手动更新：仓库 Actions 页 → Run workflow

---

## 四、常见问题

**Q: 网页打不开 / 404？**
A: 确认第 5 步构建成功（绿色 ✓）。构建成功后要等 1 分钟部署生效。

**Q: 数据是空的？**
A: 首次部署后马上打开，数据可能还没生成。等第一次构建成功后再打开，或手动 Run workflow。

**Q: 显示"加载失败：数据还没生成"？**
A: 同上，等构建成功。构建会自动生成 data/stats.json。

**Q: 想改监控关键词？**
A: 改 `sources.py` 里的 `FILTER_KEYWORDS_MUST`，然后 Actions 页手动 Run workflow。

**Q: 会不会花一分钱？**
A: 不会。GitHub 免费版：Actions 每月 2000 分钟（每天跑 3 分钟，绰绰有余）、Pages 免费、私有仓库免费。

---

## 五、本地版还在

之前电脑上的本地版（`start.command`）仍然可用，两者不冲突：
- **本地版**：实时刷新、局域网访问（Mac 开着时）
- **云端版**：随时随地、24小时在线（推荐日常用这个）
