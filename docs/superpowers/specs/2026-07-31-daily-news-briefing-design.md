# 每日资讯早报系统 — 设计文档

**日期**: 2026-07-31  
**项目**: 米桶 AI 每日资讯早报  
**版本**: v1.0

---

## 1. 概述

### 1.1 目标
开发一个自动化软件，每日定时收集多领域（AI、科技、财经等）资讯，通过 AI 智能筛选分类，生成两张 Apple 风格的信息图，并自动推送至微信公众号。

### 1.2 核心流程

```
┌─────────────┐    ┌─────────────┐    ┌─────────────────┐    ┌─────────────┐
│  资讯采集    │───→│  AI 智能筛选  │───→│   图片生成引擎   │───→│  微信推送    │
│  collector  │    │   curator   │    │    generator    │    │  publisher  │
└─────────────┘    └─────────────┘    └─────────────────┘    └─────────────┘
       ↑                                                       │
       └────────────────── 每日定时触发 (Kimi Automation) ───────┘
```

### 1.3 设计原则
- **Apple 风格**: 纯白背景、大量留白、大圆角、简洁层次、彩色圆点分类标识
- **模块化**: 采集、筛选、生图、推送四个模块独立，通过明确定义的接口通信
- **可扩展**: 新信源、新分类、新推送渠道可插件式接入
- **全自动化**: 零人工干预，从采集到推送全流程自动

---

## 2. 架构设计

### 2.1 模块划分

| 模块 | 目录 | 职责 |
|------|------|------|
| `collector` | `src/collector/` | 多源资讯采集、原始数据存储 |
| `curator` | `src/curator/` | AI 分类、去重、打分排序、摘要生成 |
| `generator` | `src/generator/` | Apple 风格图片渲染引擎 |
| `publisher` | `src/publisher/` | 微信公众号 API 推送 |
| `config` | `config/` | 信源配置、分类定义、推送设置 |
| `scheduler` | `src/scheduler/` | Kimi Blueprint Automation 定时触发接口 |

### 2.2 数据流

```
RSS/API/网页抓取 ──→ raw_news.json ──→ AI curator ──→ curated_news.json
                                                            │
                                                            ↓
                                              ┌─────────────────────┐
                                              │   generator         │
                                              │   ├── detail.png    │
                                              │   └── highlights.png│
                                              └─────────────────────┘
                                                            │
                                                            ↓
                                              wechat_material_upload
                                                            │
                                                            ↓
                                              message/custom/send
```

### 2.3 配置文件结构

```yaml
# config/sources.yaml
sources:
  - name: "机器之心"
    type: rss
    url: "https://www.jiqizhixin.com/rss"
    category_map:
      - pattern: "Agent|智能体"
        category: "Agent"
      - pattern: "GPT|LLM|模型"
        category: "模型"

  - name: "36氪"
    type: rss
    url: "https://36kr.com/feed"
    
  - name: "TechCrunch"
    type: rss
    url: "https://techcrunch.com/feed/"

# config/categories.yaml
categories:
  - id: "agent"
    name: "Agent"
    color: "#007AFF"  # Apple Blue
    priority: 1
  - id: "model"
    name: "模型"
    color: "#AF52DE"  # Apple Purple
    priority: 2
  - id: "industry"
    name: "产业"
    color: "#34C759"  # Apple Green
    priority: 3
  - id: "compute"
    name: "算力"
    color: "#FF9500"  # Apple Orange
    priority: 4
  - id: "security"
    name: "安全"
    color: "#FF3B30"  # Apple Red
    priority: 5

# config/wechat.yaml
wechat:
  app_id: "${WECHAT_APPID}"
  app_secret: "${WECHAT_APPSECRET}"
  # 首次运行时引导用户配置
```

---

## 3. 图片生成设计

### 3.1 图片 1：详细版（Detail）

| 属性 | 规格 |
|------|------|
| 尺寸 | 1242 × 2208 px（iPhone 全屏竖版） |
| 背景 | `#F5F7FA` 浅灰白，顶部微渐变至纯白 |
| 顶部栏 | "AI 早报" 品牌 + "DAILY BRIEF" 右侧 + 分隔线 |
| 标题区 | 大号 "AI早报" + 副标题 "每日精选 · 10 秒速览" + 日期 |
| 页码标记 | 右上角灰色药丸 "Top 16" |
| 内容区 | 8 条资讯，2 列 × 4 行 网格 |
| 卡片样式 | 纯白背景，`radius=24px`，极浅灰边框 `#EBEBF0` |
| 每条资讯 | 彩色圆点(6px) + 分类名 + 序号(右上角灰色) + 标题(黑 `#141415`) + 描述(灰 `#505055`) + 详情(浅灰 `#8C8C91`) + 来源(最浅灰 `#AAAAAF`) |
| 底部分隔线 | 细线 `#F0F0F5` |
| 底部品牌 | "米桶 AI · 不构成任何建议" 居中浅灰 |

### 3.2 图片 2：今日看点（Highlights）

| 属性 | 规格 |
|------|------|
| 尺寸 | 1242 × 1656 px |
| 背景 | 同详细版 `#F5F7FA` |
| 顶部栏 | 同详细版 |
| 标题区 | "AI早报" 大号 + 日期 + 标签药丸("10 秒速览", "Agent · 推理 · 算力") |
| 分区标题 | "今日看点" + 下划线(Apple Blue `#007AFF`) |
| 内容区 | 3 条重点资讯，全宽垂直卡片 |
| 卡片样式 | 纯白背景，`radius=28px`，更大更醒目 |
| 每条资讯 | 大号序号圆圈(56px) + 彩色圆点 + 分类名 + 标题(34px) + 一句话描述(20px) |
| 底部横幅 | Apple Blue 药丸 `"16 条 AI 要闻 · 2 页速览 · 10 秒看完"` + 免责文字 |
| 底部品牌 | "米桶 AI" (Blue) + "Daily Brief" (灰) |

### 3.3 技术实现

使用 Python `Pillow` 库纯代码绘制：

```python
from PIL import Image, ImageDraw, ImageFont

def generate_detail_image(news_list, date_str):
    img = Image.new('RGB', (1242, 2208), (245, 247, 250))
    draw = ImageDraw.Draw(img)
    
    # 1. 渐变背景
    draw_gradient_bg(img, top=(255,255,255), bottom=(245,247,250))
    
    # 2. 顶部栏
    draw_header(draw, brand="米桶 AI", subtitle="DAILY BRIEF")
    
    # 3. 标题区
    draw_title_block(draw, date=date_str)
    
    # 4. 资讯卡片网格 (2列×4行)
    for idx, news in enumerate(news_list[:8]):
        x, y = grid_position(idx, cols=2, card_w=540, card_h=420)
        draw_news_card(draw, x, y, news, idx+1)
    
    # 5. 底部品牌
    draw_footer(draw, brand="米桶 AI", disclaimer="不构成任何建议")
    
    return img
```

**字体栈**:
```python
# 优先使用系统字体，确保中文渲染
FONT_STACK = [
    "/Library/Fonts/Arial Unicode.ttf",           # macOS
    "/System/Library/Fonts/PingFang.ttc",         # macOS
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",  # Linux
]
```

---

## 4. 数据采集设计

### 4.1 信源类型支持

| 类型 | 实现 | 示例 |
|------|------|------|
| RSS | `feedparser` | 机器之心、36氪、TechCrunch |
| API | `requests` + JSON 解析 | 自定义 API 接口 |
| 网页抓取 | `requests` + `beautifulsoup4` | 无 RSS 的站点 |

### 4.2 采集流程

```
1. 读取 config/sources.yaml
2. 对每个信源：
   a. 请求数据（RSS feed / API / 网页）
   b. 解析为统一格式：{title, url, summary, published_at, source_name}
   c. 存入临时 JSON: data/raw/YYYY-MM-DD_raw.json
3. 去重：基于 URL MD5 + 标题相似度（Levenshtein 距离 < 0.8 视为重复）
4. 过滤：仅保留 24h 内发布的资讯
```

### 4.3 AI 筛选与分类

使用 LLM API（Kimi/OpenAI）进行：

1. **分类**: 将每条资讯归类到预定义分类（Agent/模型/产业/算力/安全）
2. **打分**: 评估每条资讯的重要性（1-10 分），考虑：时效性、影响力、热度
3. **摘要**: 生成 1 句话的"简读"解读
4. **排序**: 综合分数 + 分类多样性（确保每个类别都有代表），取 Top 16

**Prompt 模板**:
```
你是一位资深科技编辑，请对以下资讯进行分类和评估。

分类选项: Agent, 模型, 产业, 算力, 安全

对每条资讯输出 JSON:
{
  "category": "分类名",
  "score": 1-10,
  "brief": "一句话解读（50字以内）"
}

输入资讯:
{news_list}
```

---

## 5. 微信公众号推送设计

### 5.1 推送流程

```
1. 读取 config/wechat.yaml 获取 app_id, app_secret
2. 调用 GET https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential
   → 获取 access_token（有效期 7200s，需缓存）
3. 上传图片到素材库
   POST https://api.weixin.qq.com/cgi-bin/media/upload?access_token=TOKEN&type=image
   → 获取 media_id
4. 发送图文消息
   POST https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=TOKEN
   {
     "touser": "OPENID",
     "msgtype": "news",
     "news": {
       "articles": [{
         "title": "米桶 AI 早报 | 2026.07.31",
         "description": "16 条 AI 要闻 · 2 页速览 · 10 秒看完",
         "url": "https://mp.weixin.qq.com/...",
         "picurl": "上传后的图片 URL"
       }]
     }
   }
```

### 5.2 首次配置引导

当 `config/wechat.yaml` 未配置时，程序输出：
```
[首次运行] 请配置微信公众号推送：
1. 登录 https://mp.weixin.qq.com/ 获取 AppID 和 AppSecret
2. 运行: export WECHAT_APPID=your_appid
        export WECHAT_APPSECRET=your_appsecret
3. 或编辑 config/wechat.yaml
```

---

## 6. 定时调度设计

### 6.1 Kimi Work Blueprint Automation

```yaml
# automation.yaml (Kimi Work 配置)
title: "米桶 AI 每日早报"
trigger:
  kind: schedule
  cron: "0 8 * * *"   # 每天早上 8 点
  timezone: "Asia/Shanghai"
execution:
  kind: code
  runtime: python
  entryRef:
    kind: path
    base: workspace
    path: "src/main.py"
```

### 6.2 本地定时运行（备选）

使用 `crontab` 或 `systemd timer`:
```bash
# crontab -e
0 8 * * * cd /path/to/project && python3 src/main.py >> logs/cron.log 2>&1
```

---

## 7. 项目目录结构

```
ai-news-briefing/
├── README.md
├── requirements.txt
├── config/
│   ├── sources.yaml        # 信源配置
│   ├── categories.yaml     # 分类定义与配色
│   └── wechat.yaml         # 微信 API 配置（gitignored）
├── src/
│   ├── main.py             # 入口：协调全流程
│   ├── collector/
│   │   ├── __init__.py
│   │   ├── rss_fetcher.py  # RSS 采集
│   │   ├── api_fetcher.py  # API 采集
│   │   └── web_scraper.py  # 网页抓取
│   ├── curator/
│   │   ├── __init__.py
│   │   ├── dedup.py        # 去重
│   │   ├── classifier.py   # AI 分类+打分
│   │   └── ranker.py       # 排序 Top 16
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── detail_card.py  # 详细版图片
│   │   ├── highlights_card.py  # 今日看点图片
│   │   └── assets/         # 字体、图标资源
│   ├── publisher/
│   │   ├── __init__.py
│   │   └── wechat.py       # 微信推送
│   └── utils/
│       ├── __init__.py
│       ├── config_loader.py
│       └── logger.py
├── data/
│   └── raw/                # 原始采集数据
├── output/
│   └── YYYY-MM-DD/         # 每日生成的图片
└── logs/
    └── app.log
```

---

## 8. 错误处理

| 场景 | 处理策略 |
|------|---------|
| 信源请求失败 | 记录日志，跳过该信源，继续处理其他 |
| LLM API 超时 | 重试 3 次（指数退避），失败则使用规则分类 |
| 微信推送失败 | 图片保存到 output/ 目录，通知用户手动推送 |
| 字体缺失 | 降级到系统默认字体，输出警告 |
| 无资讯可推送 | 生成"今日无新资讯"占位图，避免空运行 |

---

## 9. 未来扩展

- [ ] 支持 Telegram / 钉钉 / 企业微信多渠道推送
- [ ] Kimi Work Widget 看板预览
- [ ] 用户自定义分类和信源（Web 界面）
- [ ] 资讯历史数据库 + 搜索
- [ ] 多语言支持（英文版资讯图）

---

## 10. 关键决策记录

| 决策 | 选择 | 理由 |
|------|------|------|
| 图片风格 | Apple 风格 | 用户要求"和别人有差异"，纯白简洁 |
| 品牌名 | 米桶 AI | 用户指定 |
| 架构 | 模块化 Python | 可移植、可扩展、可本地调试 |
| 调度 | Kimi Automation + 本地 cron 备选 | 灵活性 |
| 图片生成 | Pillow 纯代码绘制 | 无外部依赖，精确控制像素 |
| AI 筛选 | LLM API | 自动分类+摘要，比规则更准确 |

---

*文档由 Kimi Work brainstorming 流程生成*
