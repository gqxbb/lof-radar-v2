import os
import requests

# 自动读取你在保险箱里存的飞书长链接
FEISHU_URL = os.getenv("FEISHU_WEBHOOK")

def test_link():
    # 飞书最基础的纯文本协议，不带任何卡片排版
    payload = {
        "msg_type": "text",
        "content": {
            "text": "💡 纯净链路测试：GitHub 已经成功找到飞书！"
        }
    }
    
    print("正在向飞书发射网络探针...")
    try:
        res = requests.post(FEISHU_URL, json=payload, timeout=10)
        # 这一行会在 GitHub 日志里打印出飞书官方服务器的亲口回话
        print(f"【核心日志】飞书服务器实时返回状态码: {res.status_code}")
        print(f"【核心日志】飞书服务器实时返回内容: {res.text}")
    except Exception as e:
        print(f"❌ 跨洋网络连接彻底超时或失败: {e}")

if __name__ == "__main__":
    test_link()
