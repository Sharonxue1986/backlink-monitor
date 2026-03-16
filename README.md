# Backlink Monitor

自动化外链监控工具，监控 tenorshare.com 和 imyfone.com 的新外链。

## 🚀 快速开始

### 1. 配置 Google Alerts RSS

访问 https://www.google.com/alerts 创建以下监控：

**tenorshare 监控关键词：**
- `"tenorshare.com"`
- `"tenorshare 4ukey"`
- `"tenorshare review"`

**imyfone 监控关键词：**
- `"imyfone.com"`
- `"imyfone chatart"`
- `"imyfone review"`

设置选项：
- 频率：每天
- 来源：博客、新闻、网页
- 发送方式：RSS Feed

### 2. 更新 RSS URL

编辑 `check_backlinks.py`，替换 `ALERTS_RSS_URLS` 中的示例 URL：

```python
ALERTS_RSS_URLS = {
    "tenorshare": [
        "https://www.google.com/alerts/feeds/.../你的实际RSS地址",
    ],
    "imyfone": [
        "https://www.google.com/alerts/feeds/.../你的实际RSS地址",
    ]
}
```

### 3. 部署完成

GitHub Actions 将每天自动运行，生成外链报告。

## 📊 输出报告

- **Excel**: `reports/backlink_report_YYYYMMDD.xlsx`
- **JSON**: `reports/backlink_report_YYYYMMDD.json`

报告包含字段：
- 日期
- 品牌
- 外链标题
- 来源网站
- 预估 DR
- 外链 URL
- 关键词

## ⏰ 运行时间

- **自动运行**: 每天北京时间 17:00
- **手动运行**: 在 Actions 页面点击 "Run workflow"

## 📝 配置说明

详见 `README_GitHubActions.md`
