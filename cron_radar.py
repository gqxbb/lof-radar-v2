import os
import requests

# 自动读取你在保险箱里存的飞书长链接
FEISHU_URL = os.getenv("FEISHU_WEBHOOK")

def test_feishu():
    # 🍏 飞书开放平台智能助手最爱的标准 post 富文本格式
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "🦅 小本本 · 链路终极对齐测试",
                    "content": [
                        [
                            {
                                "tag": "text",
                                "text": "✅ 恭喜梁总！飞书通道格式已完美识别，全线彻底打通！"
                            }
                        ]
                    ]
                }
            }
        }
    }
    
    print("正在向飞书开放平台通道发射富文本探针...")
    if FEISHU_URL:
        try:
            res = requests.post(FEISHU_URL, json=payload, timeout=10)
            print(f"【核心日志】飞书服务器实时返回内容: {res.text}")
        except Exception as e:
            print(f"❌ 跨洋网络连接失败: {e}")

if __name__ == "__main__":
    test_feishu()
