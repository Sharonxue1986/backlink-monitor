#!/usr/bin/env python3
"""
外链监控脚本 - Google 搜索版
通过搜索 Google 获取最近一周的外链
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import json
import os

# 搜索配置
SEARCH_QUERIES = {
    "tenorshare": [
        "tenorshare.com",
        "tenorshare 4ukey",
        "tenorshare review",
        "tenorshare 4ddig",
        "tenorshare icarefone",
        "tenorshare ianygo"
    ],
    "imyfone": [
        "imyfone.com",
        "imyfone d-back",
        "imyfone review",
        "imyfone chatart",
        "imyfone magicmic"
    ]
}

# 时间筛选（最近一周）
TIME_FILTER = "qdr:w"  # 最近一周

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

def search_google(query, num_results=10):
    """
    搜索 Google 获取结果
    注意：这个函数需要处理反爬虫机制
    """
    try:
        # 构建搜索 URL
        search_url = f"https://www.google.com/search?q={query}&tbs={TIME_FILTER}&num={num_results}"
        
        # 设置请求头（模拟浏览器）
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # 解析搜索结果
            for g in soup.find_all('div', class_='g'):
                try:
                    title = g.find('h3').text if g.find('h3') else "No title"
                    link = g.find('a')['href'] if g.find('a') else ""
                    
                    # 清理链接
                    if link.startswith('/url?q='):
                        link = link.split('/url?q=')[1].split('&')[0]
                    
                    if link and link.startswith('http'):
                        results.append({
                            'title': title,
                            'url': link
                        })
                except:
                    continue
            
            return results
        else:
            print(f"搜索失败，状态码: {response.status_code}")
            return []
    except Exception as e:
        print(f"搜索出错: {e}")
        return []

def generate_report():
    """生成外链报告"""
    all_links = []
    today = datetime.now().strftime("%Y-%m-%d")
    
    print("🔍 开始搜索外链...")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    for brand, queries in SEARCH_QUERIES.items():
        print(f"\n📌 搜索品牌: {brand}")
        
        for query in queries:
            print(f"   关键词: {query}")
            
            # 搜索 Google
            results = search_google(query)
            
            for result in results:
                # 排除 Google 自己的页面
                if 'google.com' in result['url']:
                    continue
                
                all_links.append({
                    'date': today,
                    'brand': brand,
                    'search_keyword': query,
                    'title': result['title'],
                    'url': result['url'],
                    'source_site': result['url'].split('/')[2].replace('www.', ''),
                    'estimated_dr': estimate_dr(result['url']),
                    'keywords': extract_keywords(result['title'], brand)
                })
            
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
    excel_file = f"reports/backlink_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
    json_file = f"reports/backlink_report_{datetime.now().strftime('%Y%m%d')}.json"
    
    # 保存为 Excel
    if not df.empty:
        # 调整列顺序
        columns = ['date', 'brand', 'title', 'source_site', 'estimated_dr', 'url', 'keywords', 'search_keyword']
        df = df[[col for col in columns if col in df.columns]]
        
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"\n✅ Excel 报告已保存: {excel_file}")
        
        # 保存为 JSON
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        print(f"✅ JSON 报告已保存: {json_file}")
        
        # 打印摘要
        print("\n📊 报告摘要:")
        print(f"   发现外链: {len(df)} 个")
        for brand in df['brand'].unique():
            count = len(df[df['brand'] == brand])
            print(f"   - {brand}: {count} 个")
    else:
        print("\n⚠️ 没有发现外链")
    
    return df

if __name__ == "__main__":
    df = generate_report()
    print("\n" + "-" * 60)
    print("✅ 监控完成!")
    print("⚠️  注意: Google 搜索可能有反爬虫限制，如果频繁运行可能被封IP")
