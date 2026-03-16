#!/usr/bin/env python3
"""
外链监控脚本 - RSS Feed 版
通过 Google Alerts RSS 获取外链
"""

import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import json
import os
from bs4 import BeautifulSoup

# Google Alerts RSS Feed URLs
ALERTS_RSS_URLS = {
    "tenorshare": [
        "https://www.google.com/alerts/feeds/00693704181867916775/16572276136164822175"
    ],
    "imyfone": [
        "https://www.google.com/alerts/feeds/00693704181867916775/16572276136164821283"
    ],
    "ianygo": [
        "https://www.google.com/alerts/feeds/00693704181867916775/16078198233704014018"
    ],
    "4ddig": [
        "https://www.google.com/alerts/feeds/00693704181867916775/15883321554252704360"
    ],
    "icarefone": [
        "https://www.google.com/alerts/feeds/00693704181867916775/13054306810209588923"
    ],
    "imyfone_anyto": [
        "https://www.google.com/alerts/feeds/00693704181867916775/9718672333614377555"
    ]
}

# 预估 DR 值
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
    "youtube.com": 99,
    "facebook.com": 96,
    "twitter.com": 94,
    "linkedin.com": 98,
}

def estimate_dr(url):
    """根据域名预估 DR 值"""
    try:
        domain = re.findall(r'https?://(?:www\.)?([^/]+)', url)[0]
        return DR_ESTIMATES.get(domain, 50)
    except:
        return 50

def extract_keywords(title, brand):
    """提取关键词"""
    keywords = [brand]
    title_lower = title.lower()
    
    common_keywords = ["review", "tutorial", "guide", "alternative", "vs", "comparison", "download", "free"]
    for kw in common_keywords:
        if kw in title_lower:
            keywords.append(kw)
    
    return ", ".join(keywords)

def fetch_rss_feed(rss_url, brand, days=7):
    """从 RSS Feed 获取外链"""
    try:
        feed = feedparser.parse(rss_url)
        new_links = []
        cutoff_date = datetime.now() - timedelta(days=days)
        
        print(f"   解析 RSS: {rss_url[:50]}...")
        print(f"   找到 {len(feed.entries)} 个条目")
        
        for entry in feed.entries:
            try:
                published = datetime(*entry.published_parsed[:6])
                if published >= cutoff_date:
                    # 从 summary 中提取链接
                    summary = entry.get('summary', '')
                    
                    # 解析 HTML
                    soup = BeautifulSoup(summary, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links:
                        url = link['href']
                        # 清理 Google 跳转链接
                        if '/url?q=' in url:
                            url = url.split('/url?q=')[1].split('&')[0]
                        
                        # 排除 Google 和非 http 链接
                        if url and url.startswith('http') and 'google.com' not in url and 'youtube.com' not in url:
                            new_links.append({
                                'date': published.strftime("%Y-%m-%d"),
                                'brand': brand,
                                'title': entry.title,
                                'url': url,
                                'source_site': url.split('/')[2].replace('www.', ''),
                                'estimated_dr': estimate_dr(url),
                                'keywords': extract_keywords(entry.title, brand)
                            })
            except Exception as e:
                print(f"   解析条目出错: {e}")
                continue
        
        return new_links
    except Exception as e:
        print(f"Error fetching RSS {rss_url}: {e}")
        return []

def generate_report():
    """生成外链报告"""
    all_links = []
    
    print("🔍 开始抓取 RSS Feed...")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    for brand, rss_urls in ALERTS_RSS_URLS.items():
        print(f"\n📌 抓取品牌: {brand}")
        
        for rss_url in rss_urls:
            # 抓取 RSS
            links = fetch_rss_feed(rss_url, brand)
            all_links.extend(links)
            
            print(f"   ✅ 发现 {len(links)} 个外链")
            
            # 延迟，避免被封
            time.sleep(2)
    
    # 去重
    seen_urls = set()
    unique_links = []
    for link in all_links:
        if link['url'] not in seen_urls:
            seen_urls.add(link['url'])
            unique_links.append(link)
    
    # 创建 DataFrame
    df = pd.DataFrame(unique_links)
    
    # 确保目录存在
    os.makedirs("reports", exist_ok=True)
    
    # 生成文件名
    today = datetime.now().strftime("%Y%m%d")
    excel_file = f"reports/backlink_report_{today}.xlsx"
    json_file = f"reports/backlink_report_{today}.json"
    
    # 保存为 Excel
    if not df.empty:
        # 调整列顺序
        columns = ['date', 'brand', 'title', 'source_site', 'estimated_dr', 'url', 'keywords']
        df = df[[col for col in columns if col in df.columns]]
        
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ Excel 报告已保存: {excel_file}")
        
        # 保存为 JSON
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        print(f"✅ JSON 报告已保存: {json_file}")
        
        # 打印摘要
        print("\n📊 报告摘要:")
        print(f"   总外链: {len(df)} 个")
        print(f"   去重后: {len(unique_links)} 个")
        for brand in df['brand'].unique():
            count = len(df[df['brand'] == brand])
            print(f"   - {brand}: {count} 个")
    else:
        print("\n⚠️ 没有发现新外链")
    
    return df

if __name__ == "__main__":
    print("=" * 70)
    print("🔍 Google Alerts RSS 外链监控")
    print("=" * 70)
    print()
    
    df = generate_report()
    
    print("\n" + "=" * 70)
    print("✅ 监控完成!")
    print("=" * 70)
