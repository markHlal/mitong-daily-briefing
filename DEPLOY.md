# 🚀 米桶 AI 每日资讯早报 — 部署指南

## 项目概述

本项目是一个自动化资讯收集与早报生成系统：
- **每日定时** 从多个 RSS 源采集资讯
- **AI 智能分类** 为科技、财经、国际等类别
- **自动生成** 2 张 Apple 风格早报图片（详细版 + 今日看点）
- **静态网站展示** 历史记录，支持浏览往期早报
- **微信公众号推送** 支持（可选）

## 部署方式：GitHub Pages + GitHub Actions（推荐）

### 第一步：在 GitHub 创建仓库

1. 打开 [github.com/new](https://github.com/new)
2. 仓库名称填写：`mitong-daily-briefing`（或其他你喜欢的名字）
3. 选择 **Public**（公开仓库，GitHub Pages 免费托管）
4. 不要勾选 "Add a README file"
5. 点击 **Create repository**

### 第二步：推送代码到 GitHub

在本地项目目录中执行以下命令：

```bash
# 进入项目目录
cd /Users/huang/Documents/Kimi/Workspaces/ai新闻收集

# 添加远程仓库（将 YOUR_USERNAME 替换为你的 GitHub 用户名）
git remote add origin https://github.com/YOUR_USERNAME/mitong-daily-briefing.git

# 推送代码
git branch -M main
git push -u origin main
```

### 第三步：配置 Kimi API Key（必须）

1. 在 GitHub 仓库页面，点击 **Settings**
2. 左侧菜单选择 **Secrets and variables → Actions**
3. 点击 **New repository secret**
4. 名称填写：`KIMI_API_KEY`
5. 值填写：你的 Kimi API Key
6. 点击 **Add secret**

> 💡 如果没有 Kimi API Key，可以在 [platform.moonshot.cn](https://platform.moonshot.cn) 申请。
> 项目也支持不使用 API Key（会回退到规则分类器），但分类准确度会降低。

### 第四步：启用 GitHub Pages

1. 在 GitHub 仓库页面，点击 **Settings**
2. 左侧菜单选择 **Pages**
3. **Source** 选择 **GitHub Actions**
4. 无需其他操作，工作流会自动处理部署

### 第五步：触发首次部署

1. 在 GitHub 仓库页面，点击 **Actions**
2. 找到 **Deploy Daily Briefing Website** 工作流
3. 点击 **Run workflow** → 再点绿色 **Run workflow** 按钮
4. 等待约 2-3 分钟，部署完成后会显示绿色 ✅

### 第六步：访问你的网站

部署完成后，网站地址为：
```
https://YOUR_USERNAME.github.io/mitong-daily-briefing/
```

## 自动化运行说明

| 触发方式 | 说明 |
|---------|------|
| ⏰ 定时触发 | 每天北京时间 08:00 自动运行 |
| 🔄 代码推送 | 每次 push 到 main 分支时触发 |
| 👆 手动触发 | 在 Actions 页面点击 Run workflow |

## 项目结构

```
.
├── config/              # 配置文件
│   ├── sources.yaml     # RSS 订阅源
│   └── categories.yaml  # 分类规则
├── src/                 # 源代码
│   ├── collector/       # RSS 采集器
│   ├── curator/         # 分类器
│   ├── generator/       # 图片生成器 + 网站生成器
│   ├── publisher/       # 推送模块
│   └── main.py          # 主入口
├── tests/               # 测试用例
├── output/              # 生成的图片
├── website/             # 静态网站输出
└── .github/workflows/   # GitHub Actions 配置
```

## 常见问题

### Q1: 网站没有更新？
- 检查 Actions 页面是否有运行失败的记录（红色 ❌）
- 确认 `KIMI_API_KEY` Secret 已正确配置
- 查看日志中的具体错误信息

### Q2: 如何修改定时时间？
编辑 `.github/workflows/deploy.yml` 中的 cron 表达式：
```yaml
schedule:
  - cron: '0 0 * * *'    # 每天 08:00 (UTC+8)
  - cron: '0 9 * * *'    # 每天 17:00 (UTC+8)
```

### Q3: 如何添加新的 RSS 源？
编辑 `config/sources.yaml` 文件，添加新的 source 配置，然后 push 到 GitHub。

### Q4: 分类不准确怎么办？
- 编辑 `config/categories.yaml` 调整分类规则
- 确保 `KIMI_API_KEY` 已配置（LLM 分类比规则分类更准确）

### Q5: 图片风格可以修改吗？
可以，编辑 `src/generator/image_generator.py` 中的样式配置：
- 字体大小
- 颜色方案
- 卡片布局
- 阴影效果

---

**部署完成后，每天早 8 点会自动生成新的资讯早报并更新网站！** 🎉

---
Deployed on GitHub Pages ✓
