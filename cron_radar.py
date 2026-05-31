import akshare as ak
import os
import datetime
from datetime import timezone, timedelta
import requests

# 强行忽略代理
os.environ['NO_PROXY'] = 'eastmoney.com,sinajs.cn'

# 🍏 从 GitHub 保险箱里自动读取关联的微信 PushKey
PUSH_KEY = os.getenv("PUSHDEER_KEY")

def run_radar():
    SHA_TZ = timezone(timedelta(hours=8))
    now = datetime.datetime.now(SHA_TZ)
    current_time = now.strftime("%Y-%m-%d %H:%M")
    
    # 【注】测试期间先不拦截周末，方便梁总今晚直接看效果
    # if now.weekday() >= 5:
    #     return

    try:
        # 抓取实时LOF行情
        fund_df = ak.fund_lof_spot_em()
    except Exception as e:
        print(f"数据源获取失败: {e}")
        return

    if fund_df is not None and not fund_df.empty:
        overseas_keywords = ["纳斯", "标普", "原油", "油气", "商品", "互联", "中概", "日经", "德国", "法国", "印度", "越南", "亚洲", "全球", "海外"]
        
        # 🍏 临时将门槛降低到 0.0%，确保今晚休市状态下，依然能把最近一个交易日达标的数据强行抓出来发送！
        premium_threshold = 0.0 
        
        count_target = 0
        group_markdown = f"## 🦅 搞钱小本本 · 微信自动套利内参\n"
        group_markdown += f"> 📡 全网云端扫盘时间：{current_time}\n"
        group_markdown += f"> ⚡ **战术提醒**：当前进入14:30盲区黄金决战期，请密切留意价差！\n\n"
        group_markdown += "─" * 15 + "\n\n"
        
        for index, row in fund_df.iterrows():
            code = str(row['基金代码'])
            name = row['基金简称']
            is_overseas = any(keyword in name for keyword in overseas_keywords) or code.startswith("1611") or code.startswith("1649") or code.startswith("501")
            
            if is_overseas:
                try:
                    premium = float(row['溢价率'])
                    if premium >= premium_threshold:
                        try:
                            limit_info = ak.fund_open_format_xw()
                            matched_fund = limit_info[limit_info['基金代码'] == code]
                            status_desc = matched_fund.iloc[0]['申购状态'] if not matched_fund.empty else "开放申购"
                        except:
                            status_desc = "开放申购"

                        if "暂停申购" in status_desc or "停申" in status_desc or status_desc == "暂停":
                            continue
                            
                        count_target += 1
                        price = float(row['现价'])
                        raw_amount = float(row.get('成交额', 0.0))
                        amount_wan = raw_amount if code.startswith("50") else raw_amount / 10000.0
                        
                        group_markdown += f"🔥 **{count_target}. 【{name}】({code})**\n"
                        group_markdown += f"> • 实时溢价率：**{premium:.2f}%**\n"
                        group_markdown += f"> • 场内现价：{price:.3f}元 | 成交额：{amount_wan:.2f}万元\n"
                        group_markdown += f"> • 场外申购：**✅ {status_desc}**\n\n"
                except:
                    continue

        if count_target == 0:
            group_markdown += "⚖️ **📊 盘中扫描**：当前市场平稳，暂未出现符合套利门槛的疯狂品种。\n"
        else:
            group_markdown += "─" * 15 + "\n"
            group_markdown += f"💡 **套利纪律**：请在 15:00 前完成场外下单。注意防范小成交额冲击成本！"

        # 🍏 强行向 PushDeer 微信通道发射
        if PUSH_KEY:
            payload = {
                "pushkey": PUSH_KEY,
                "text": "🦅 搞钱小本本 · 决战内参已送达", # 微信弹窗看到的简略标题
                "desp": group_markdown,                # 点击进去看到的完整精美Markdown表格
                "type": "markdown"
            }
            res = requests.post("https://api2.pushdeer.com/message/push", data=payload)
            print(f"微信通道返回状态: {res.text}")

if __name__ == "__main__":
    run_radar()
