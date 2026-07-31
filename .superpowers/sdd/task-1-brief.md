# Task 1: 项目脚手架 + 配置系统 + 日志工具

**项目**: 米桶 AI 每日资讯早报系统  
**工作目录**: `/Users/huang/Documents/Kimi/Workspaces/ai新闻收集`

这是整个项目的第一个任务，建立基础框架。后续所有模块都依赖这些基础设施。

---

## 需要创建的文件

1. `requirements.txt` — Python 依赖
2. `src/utils/__init__.py` — 空文件
3. `src/utils/config_loader.py` — YAML 配置加载器
4. `src/utils/logger.py` — 日志工具
5. `src/collector/__init__.py` — 空文件
6. `src/curator/__init__.py` — 空文件
7. `src/generator/__init__.py` — 空文件
8. `src/publisher/__init__.py` — 空文件
9. `config/sources.yaml` — 信源配置
10. `config/categories.yaml` — 分类配置
11. `config/wechat.yaml` — 微信配置
12. `tests/test_config.py` — 配置系统测试
13. `data/raw/.gitkeep` — 占位
14. `output/.gitkeep` — 占位
15. `logs/.gitkeep` — 占位

## 目录结构

```
src/
├── collector/
│   └── __init__.py
├── curator/
│   └── __init__.py
├── generator/
│   └── __init__.py
├── publisher/
│   └── __init__.py
└── utils/
    ├── __init__.py
    ├── config_loader.py
    └── logger.py
```

## 代码要求

### config_loader.py

```python
import os
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def load_config(rel_path: str) -> dict:
    path = PROJECT_ROOT / "config" / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_sources() -> list[dict]:
    cfg = load_config("sources.yaml")
    return cfg.get("sources", [])


def load_categories() -> list[dict]:
    cfg = load_config("categories.yaml")
    return cfg.get("categories", [])


def load_wechat_config() -> dict:
    cfg = load_config("wechat.yaml")
    wechat = cfg.get("wechat", {})
    wechat["app_id"] = os.getenv("WECHAT_APPID", wechat.get("app_id", ""))
    wechat["app_secret"] = os.getenv("WECHAT_APPSECRET", wechat.get("app_secret", ""))
    return wechat
```

### logger.py

```python
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)

    fmt = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    fh = logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(fmt)
    logger.addHandler(ch)

    return logger
```

### requirements.txt

```text
feedparser>=6.0.0
requests>=2.31.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
PyYAML>=6.0
python-dotenv>=1.0.0
pytest>=7.4.0
```

### config/sources.yaml

```yaml
sources:
  - name: "机器之心"
    type: rss
    url: "https://www.jiqizhixin.com/rss"
    enabled: true

  - name: "量子位"
    type: rss
    url: "https://www.qbitai.com/feed"
    enabled: true

  - name: "36氪"
    type: rss
    url: "https://36kr.com/feed"
    enabled: true

  - name: "TechCrunch"
    type: rss
    url: "https://techcrunch.com/feed/"
    enabled: false
```

### config/categories.yaml

```yaml
categories:
  - id: "agent"
    name: "Agent"
    color: "#007AFF"
    priority: 1
  - id: "model"
    name: "模型"
    color: "#AF52DE"
    priority: 2
  - id: "industry"
    name: "产业"
    color: "#34C759"
    priority: 3
  - id: "compute"
    name: "算力"
    color: "#FF9500"
    priority: 4
  - id: "security"
    name: "安全"
    color: "#FF3B30"
    priority: 5
```

### config/wechat.yaml

```yaml
wechat:
  app_id: ""
  app_secret: ""
```

### tests/test_config.py

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils.config_loader import load_sources, load_categories, load_wechat_config


def test_load_sources():
    sources = load_sources()
    assert isinstance(sources, list)
    assert len(sources) > 0
    for s in sources:
        assert "name" in s
        assert "url" in s


def test_load_categories():
    cats = load_categories()
    assert isinstance(cats, list)
    assert len(cats) > 0
    for c in cats:
        assert "id" in c
        assert "name" in c
        assert "color" in c


def test_load_wechat_empty():
    cfg = load_wechat_config()
    assert "app_id" in cfg
    assert "app_secret" in cfg
```

## 执行步骤

1. 创建目录: `mkdir -p src/{collector,curator,generator,publisher,utils} tests config data/raw output logs`
2. 安装依赖: `pip install -r requirements.txt`
3. 创建所有文件（内容如上）
4. 运行测试: `pytest tests/test_config.py -v`
5. 全部通过后 commit: `git add -A && git commit -m "feat: project scaffold, config system, logger"`

## 全局约束

- Python >= 3.10
- 禁止硬编码密钥
- 微信配置通过环境变量 WECHAT_APPID / WECHAT_APPSECRET 注入
- 日志输出到 `logs/app.log`

---
**注意**: 请严格按照上述代码实现，不要添加计划之外的功能。测试必须全部通过后才能提交。
