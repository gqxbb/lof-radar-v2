import os
import requests

# 自动读取新家保险箱里的 DING_WEBHOOK
GROUP_WEBHOOK = os.getenv("DING_WEBHOOK")

def run_radar():
    group_markdown = f"## 🦅 搞钱小本本 · 钉钉机器人联通测试\n"
    group_markdown += f"> 📡 状态：GitHub Actions 换家重构链路测试\n\n"
    group_markdown += "─" * 20 + "\n\n"
    group_markdown += f"🔥 **1. 【完美合体标的】(888888)**\n"
    group_markdown += f"> • 盘中实时溢价率：**+100% 满格信号**\n"
    group_markdown += f"> • 物理链路状态：**✅ 恭喜梁总，破防换家成功，全线彻底打通！**\n\n"
    group_markdown += "─" * 20 + "\n"
    group_markdown += f"💡 明天（周一）下午 14:30，新雷达将全自动接管真实行情扫盘！"

    if GROUP_WEBHOOK:
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": "🦅 搞钱小本本关联成功",
                "text": group_markdown
            }
        }
        res = requests.post(GROUP_WEBHOOK, json=payload)
        print(f"钉钉接口返回内容: {res.text}")

if __name__ == "__main__":
    run_radar()
