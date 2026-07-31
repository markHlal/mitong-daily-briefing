# Task 2 执行报告

## 创建的文件列表

1. `src/collector/rss_fetcher.py` — RSS 采集器，负责解析 RSS feed、清洗摘要、过滤 48 小时内资讯
2. `src/collector/dedup.py` — 去重器，基于 URL MD5 哈希 + 标题相似度去重
3. `tests/test_collector.py` — 测试文件，覆盖 URL 去重、相似标题去重、HTML 摘要清洗

## 测试运行结果

```
$ python -m pytest tests/test_collector.py -v
============================= test session starts ==============================
platform darwin -- Python 3.12.13, pytest-9.1.1, pluggy-9.1.1
rootdir: /Users/huang/Documents/kimi/Workspaces/ai新闻收集
collected 3 items

tests/test_collector.py::test_deduplicate_by_url PASSED                  [ 33%]
tests/test_collector.py::test_deduplicate_by_similar_title PASSED        [ 66%]
tests/test_collector.py::test_clean_summary PASSED                       [100%]

============================== 3 passed in 0.06s ===============================
```

## 是否全部通过

✅ 全部 3 个测试通过

## 遇到的问题及解决方案

### 问题：brief 中 dedup.py 的 `_title_similarity` 使用字符级 SequenceMatcher，导致 `test_deduplicate_by_url` 失败

- **现象**: `test_deduplicate_by_url` 中 "News A" 与 "News B" 的字符级相似度为 0.9（> 0.8），被误判为重复，导致只返回 1 条结果（期望 2 条）
- **根因**: 字符级 SequenceMatcher 对短标题过于敏感，"News A" 和 "News B" 只有最后一个字符不同，相似度高达 0.9
- **解决方案**: 将 `_title_similarity` 改为词级（word-level）比较，即 `SequenceMatcher(None, a.split(), b.split()).ratio()`
  - "News A".split() vs "News B".split() → ratio ≈ 0.5（< 0.8，保留）✓
  - "Apple releases iOS 18".split() vs "Apple releases iOS 18 today".split() → ratio = 8/9 ≈ 0.889（> 0.8，去重）✓
- **影响范围**: 仅修改 `src/collector/dedup.py` 第 14 行，未添加额外功能，符合"不要添加额外功能"的约束

## Git Commit Hash

`9dbc031c5af25a6ee39d7e7a475e725c93c58c86`

## 状态

**DONE**
