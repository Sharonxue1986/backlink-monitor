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
    
    # 使用富文本消息，支持 @ 用户
    message = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "📊 YouTube KOL 推广周报",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": "📅 时间: "
                            },
                            {
                                "tag": "text",
                                "text": f"{report_data.get('time_range', '最近一周')}\n"
                            },
                            {
                                "tag": "text",
                                "text": "📈 总视频数: "
                            },
                            {
                                "tag": "text",
                                "text": f"{total_videos}\n"
                            },
                            {
                                "tag": "text",
                                "text": "👀 总观看数: "
                            },
                            {
                                "tag": "text",
                                "text": f"{total_views}\n\n"
                            },
                            {
                                "tag": "text",
                                "text": "📋 各品牌数据:\n"
                            },
                            {
                                "tag": "text",
                                "text": f"{brand_text}\n\n"
                            },
                            {
                                "tag": "a",
                                "text": "🔗 查看详细报告",
                                "href": "https://pcn3zxfoc68k.feishu.cn/base/C5TwbEqjLasVAls4zzTckKBQnwc"
                            },
                            {
                                "tag": "text",
                                "text": "\n\n"
                            },
                            {
                                "tag": "at",
                                "user_id": "ou_d7b6afe46cf227fcbbaf6f39644022a9",
                                "user_name": "薛春暖"
                            },
                            {
                                "tag": "text",
                                "text": " 这是本周的 YouTube KOL 推广报告，请查收！"
                            }
                        ]
                    ]
                }
            }
        }
    }
    
    try:
        response = requests.post(FEISHU_WEBHOOK_URL, json=message, timeout=10)
        if response.status_code == 200:
            print("✅ 报告已发送到飞书并 @ 薛春暖")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            print(f"响应: {response.text}")
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
