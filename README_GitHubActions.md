# GitHub Actions 外链监控配置指南

## 📦 已创建的文件

1. `.github/workflows/backlink-monitor.yml` - GitHub Actions 工作流
2. `check_backlinks.py` - 外链监控脚本

## 🔧 配置步骤

### 步骤 1: 创建 GitHub 仓库

1. 在 GitHub 上创建新仓库（例如：`backlink-monitor`）
2. 将以下文件上传到仓库：
   - `.github/workflows/backlink-monitor.yml`
   - `check_backlinks.py`
   - `README.md`（可选）

### 步骤 2: 设置 Google Alerts

1. 访问 https://www.google.com/alerts
2. 创建以下监控关键词：

#### tenorshare 监控
- `"tenorshare.com"`
- `"tenorshare 4ukey"`
- `"tenorshare review"`
- `"tenorshare 4ddig"`
- `"tenorshare icarefone"`
- `"tenorshare ianygo"`

#### imyfone 监控
- `"imyfone.com"`
- `"imyfone d-back"`
- `"imyfone review"`
- `"imyfone chatart"`
- `"imyfone magicmic"`

3. 设置选项：
   - **频率**: 每天
   - **来源**: 博客、新闻、网页
   - **语言**: 所有语言
   - **地区**: 所有地区
   - **数量**: 所有结果
   - **发送方式**: RSS Feed

4. 获取 RSS URL：
   - 创建 Alert 后，点击 RSS 图标
   - 复制 RSS Feed URL

### 步骤 3: 更新脚本中的 RSS URL

编辑 `check_backlinks.py` 文件，更新 `ALERTS_RSS_URLS`：

```python
ALERTS_RSS_URLS = {
    "tenorshare": [
        "https://www.google.com/alerts/feeds/.../tenorshare",  # 替换为实际的 RSS URL
        "https://www.google.com/alerts/feeds/.../4ukey",
    ],
    "imyfone": [
        "https://www.google.com/alerts/feeds/.../imyfone",  # 替换为实际的 RSS URL
        "https://www.google.com/alerts/feeds/.../chatart",
    ]
}
```

### 步骤 4: 提交到 GitHub

```bash
git add .
git commit -m "Initial backlink monitor setup"
git push origin main
```

### 步骤 5: 验证运行

1. 进入 GitHub 仓库
2. 点击 "Actions" 标签
3. 找到 "Backlink Monitor" 工作流
4. 点击 "Run workflow" 手动触发测试

## 📊 输出结果

每次运行后，会在 `reports/` 目录生成：

1. **Excel 报告**: `backlink_report_YYYYMMDD.xlsx`
   - 日期
   - 品牌
   - 外链标题
   - 来源网站
   - 预估 DR
   - 外链 URL
   - 关键词

2. **JSON 报告**: `backlink_report_YYYYMMDD.json`
   - 结构化数据，便于程序处理

## ⏰ 运行频率

- **自动运行**: 每天 UTC 9:00（北京时间 17:00）
- **手动运行**: 可随时在 Actions 页面点击 "Run workflow"

## 🔔 通知设置（可选）

如需邮件通知，修改 `.github/workflows/backlink-monitor.yml`：

```yaml
- name: Send email notification
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 587
    username: ${{ secrets.EMAIL_USERNAME }}
    password: ${{ secrets.EMAIL_PASSWORD }}
    subject: Backlink Report ${{ github.run_date }}
    to: your-email@example.com
    attachments: reports/backlink_report_*.xlsx
```

## 📝 自定义配置

### 添加更多监控品牌

在 `check_backlinks.py` 中添加：

```python
ALERTS_RSS_URLS = {
    "tenorshare": [...],
    "imyfone": [...],
    "your-brand": [
        "https://www.google.com/alerts/feeds/.../your-brand",
    ]
}

BRAND_KEYWORDS = {
    "tenorshare": [...],
    "imyfone": [...],
    "your-brand": ["keyword1", "keyword2"]
}
```

### 修改监控频率

编辑 `.github/workflows/backlink-monitor.yml`：

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时运行一次
```

Cron 表达式参考：
- `0 9 * * *` - 每天 9:00
- `0 */6 * * *` - 每6小时
- `0 9 * * 1` - 每周一 9:00

## 🐛 故障排除

### 问题：没有生成报告
- 检查 RSS URL 是否正确配置
- 检查 Google Alerts 是否有新内容
- 查看 Actions 日志获取错误信息

### 问题：DR 预估不准确
- 在 `DR_ESTIMATES` 字典中添加更多网站
- 或使用真实 DR API（需要 API key）

## 📄 许可证

MIT License
