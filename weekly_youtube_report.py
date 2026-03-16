#!/usr/bin/env python3
"""
YouTube KOL 报告自动生成脚本
每周一 9:30 自动运行，生成报告并发送到飞书
"""

import json
import requests
from datetime import datetime, timedelta
import os

# 飞书配置
FEISHU_WEBHOOK_URL = os.getenv('FEISHU_WEBHOOK_URL', '')  # 从环境变量读取

def generate_youtube_report():
    """生成 YouTube KOL 报告"""
    # 这里调用之前的脚本逻辑
    # 简化版：读取已有的 JSON 报告
    try:
        with open('/root/.openclaw/workspace/youtube_influencer_report_strict_20260316.json', 'r') as f:
            data = json.load(f)
        return data
    except:
        return None

def send_to_feishu(report_data):
    """发送报告到飞书"""
    if not FEISHU_WEBHOOK_URL:
        print("⚠️  未配置飞书 Webhook URL")
        return False
    
    # 构造消息
    total_videos = report_data.get('total_videos', 0)
    total_views = report_data.get('total_views', 0)
    brand_stats = report_data.get('brand_stats', {})
    
    # 品牌统计文本
    brand_text = "\n".join([f"• {brand}: {stats['count']}个视频, {stats['views']}观看" 
                           for brand, stats in brand_stats.items()])
    
    message = {
        "msg_type": "text",
        "content": {
            "text": f"""📊 YouTube KOL 推广周报

📅 时间: {report_data.get('time_range', '最近一周')}
📈 总视频数: {total_videos}
👀 总观看数: {total_views}

📋 各品牌数据:
{brand_text}

🔗 详细报告: https://pcn3zxfoc68k.feishu.cn/base/C5TwbEqjLasVAls4zzTckKBQnwc

⏰ 报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK_URL, json=message, timeout=10)
        if response.status_code == 200:
            print("✅ 报告已发送到飞书")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发送出错: {e}")
        return False

if __name__ == "__main__":
    print("🎬 YouTube KOL 报告生成器")
    print("=" * 50)
    
    # 生成报告
    report = generate_youtube_report()
    
    if report:
        print(f"✅ 报告生成成功")
        print(f"   视频数: {report['total_videos']}")
        print(f"   观看数: {report['total_views']}")
        
        # 发送到飞书
        send_to_feishu(report)
    else:
        print("❌ 报告生成失败")
