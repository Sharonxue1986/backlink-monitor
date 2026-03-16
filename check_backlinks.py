#!/usr/bin/env python3
"""
外链监控脚本
监控 tenorshare.com 和 imyfone.com 的新外链
"""

import feedparser
import pandas as pd
from datetime import datetime, timedelta
import os
import re
import json

# Google Alerts RSS Feed URLs
# 注意：需要替换为实际的 RSS URL
ALERTS_RSS_URLS = {
    "tenorshare": [
        # 示例格式，需要替换为实际的 RSS URL
        # "https://www.google.com/alerts/feeds/.../tenorshare",
    ],
    "imyfone": [
        # 示例格式，需要替换为实际的 RSS URL
        # "https://www.google.com/alerts/feeds/.../imyfone",
    ]
}

# 品牌关键词配置
BRAND_KEYWORDS = {
    "tenorshare": ["tenorshare", "4ukey", "4ddig", "icarefone", "ianygo"],
    "imyfone": ["imyfone", "chatart", "magicmic", "d-back", "ulmate"]
}

# 预估 DR 值 (基于网站类型)
DR_ESTIMATES = {
    "techradar.com": 91,
    "cnet.com": 93,
    "pcmag.com": 89,
    "9to5mac.com": 85,
    "macrumors.com": 86,
    "makeuseof.com": 84,
    "appleinsider.com": 82,
    "imore.com": 78,
    "producthunt.com": 90,
    "reddit.com": 95,
    "trustpilot.com": 94,
    "medium.com": 93,
    "quora.com": 92,
    "g2.com": 88,
    "softpedia.com": 87,
    "alternativeto.net": 83,
    "wikihow.com": 88,
    "ifixit.com": 84,
    "guidingtech.com": 77,
    "techjunkie.com": 76,
    "igeeksblog.com": 74,
    "fonearena.com": 71,
    "gizchina.com": 75,
    "cultofmac.com": 79,
}

def estimate_dr(url):
    """根据域名预估 DR 值"""
    domain = re.findall(r'https?://([^/]+)', url)
    if domain:
        domain = domain[0].replace('www.', '')
        return DR_ESTIMATES.get(domain, 50)  # 默认50
    return 50

def extract_keywords(title, brand):
    """提取关键词"""
    keywords = []
    title_lower = title.lower()
    
    # 品牌关键词
    for kw in BRAND_KEYWORDS.get(brand, []):
        if kw in title_lower:
            keywords.append(kw)
    
    # 通用关键词
    common_keywords = ["review", "tutorial", "guide", "alternative", "vs", "comparison"]
    for kw in common_keywords:
        if kw in title_lower:
            keywords.append(kw)
    
    return ", ".join(keywords) if keywords else brand

def fetch_google_alerts(rss_url, days=7):
    """从 Google Alerts RSS 抓取外链"""
    try:
        feed = feedparser.parse(rss_url)
        new_links = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for entry in feed.entries:
            try:
                published = datetime(*entry.published_parsed[:6])
                if published >= cutoff_date:
                    # 从 summary 中提取实际链接
                    summary = entry.get('summary', '')
                    urls = re.findall(r'href=["\'](https?://[^"\']+)["\']', summary)
                    
                    for url in urls:
                        new_links.append({
                            "title": entry.title,
                            "url": url,
                            "published": published.strftime("%Y-%m-%d"),
                            "source": rss_url
                        })
            except:
                continue
        
        return new_links
    except Exception as e:
        print(f"Error fetching {rss_url}: {e}")
        return []

def generate_report():
    """生成外链报告"""
    all_links = []
    
    # 从 RSS 抓取
    for brand, urls in ALERTS_RSS_URLS.items():
        for rss_url in urls:
            if rss_url:  # 确保 URL 不为空
                links = fetch_google_alerts(rss_url)
                for link in links:
                    link["brand"] = brand
                    link["estimated_dr"] = estimate_dr(link["url"])
                    link["keywords"] = extract_keywords(link["title"], brand)
                    all_links.append(link)
    
    # 如果没有 RSS 数据，使用示例数据（实际使用时删除）
    if not all_links:
        print("警告: 没有配置 RSS URL，请更新 ALERTS_RSS_URLS")
        # 示例数据
        all_links = [
            {
                "date": "2026-03-15",
                "brand": "tenorshare",
                "title": "Tenorshare 4uKey Review 2026",
                "source_site": "TechRadar",
                "estimated_dr": 91,
                "url": "https://www.techradar.com/reviews/tenorshare-4ukey",
                "keywords": "4ukey, review"
            },
            {
                "date": "2026-03-14",
                "brand": "imyfone",
                "title": "iMyFone ChatArt AI Review",
                "source_site": "Product Hunt",
                "estimated_dr": 90,
                "url": "https://www.producthunt.com/products/imyfone-chatart",
                "keywords": "chatart, AI, review"
            }
        ]
    
    # 创建 DataFrame
    df = pd.DataFrame(all_links)
    
    # 确保目录存在
    os.makedirs("reports", exist_ok=True)
    
    # 生成文件名
    today = datetime.now().strftime("%Y%m%d")
    excel_file = f"reports/backlink_report_{today}.xlsx"
    json_file = f"reports/backlink_report_{today}.json"
    
    # 保存为 Excel
    if not df.empty:
        # 调整列顺序
        columns = ["date", "brand", "title", "source_site", "estimated_dr", "url", "keywords"]
        df = df[[col for col in columns if col in df.columns]]
        
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"✅ Excel 报告已保存: {excel_file}")
        
        # 保存为 JSON
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        print(f"✅ JSON 报告已保存: {json_file}")
        
        # 打印摘要
        print("\n📊 报告摘要:")
        print(f"   发现新外链: {len(df)} 个")
        if 'brand' in df.columns:
            for brand in df['brand'].unique():
                count = len(df[df['brand'] == brand])
                print(f"   - {brand}: {count} 个")
    else:
        print("⚠️ 没有发现新外链")
    
    return df

if __name__ == "__main__":
    print("🔍 开始监控外链...")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    df = generate_report()
    
    print("-" * 60)
    print("✅ 监控完成!")
