import os
import requests

GROUP_WEBHOOK = os.getenv("DING_WEBHOOK")

def run_radar():
    # 开头直接顶格写“测试”两个字，让钉钉防火墙瞬间高潮放行！
    group_markdown = "测试：搞钱小本本通道已彻底打通！"

    if GROUP_WEBHOOK:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "测试通知",
                "text": group_markdown
            }
        }
        res = requests.post(GROUP_WEBHOOK, json=payload)
        print(f"钉钉接口返回状态码: {res.status_code}, 返回内容: {res.text}")

if __name__ == "__main__":
    run_radar()
