import streamlit as st
import akshare as ak
import datetime
from datetime import timezone, timedelta
import pandas as pd

# 🍏 强制让 Streamlit 页面横向铺满，并设置高大上的暗夜蓝主题
st.set_page_config(page_title="🦅 搞钱小本本 · LOF雷达", layout="wide")

# 强制注入高端暗夜黑客风格 CSS 样式
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; color: #ecf0f1; }
    .stButton>button {
        background-color: #ff4b4b; color: white; width: 100%; 
        font-size: 20px; font-weight: bold; border-radius: 10px; height: 50px;
    }
    .fund-card {
        background-color: #1f242d; padding: 20px; border-radius: 10px; 
        border-left: 5px solid #ff4b4b; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🦅 搞钱小本本 · 盘中盲区黄金决战雷达")
st.subheader("💡 战术提醒：每天 14:30 - 14:50 之间点击下方大按钮，精准捕捉跨国套利肉票！")

# 👑 黄金居中、极其醒目的一键刷新大按钮
if st.button("🔄 立即刷新全市场 LOF 溢价数据并生成内参"):
    SHA_TZ = timezone(timedelta(hours=8))
    current_time = datetime.datetime.now(SHA_TZ).strftime("%Y-%m-%d %H:%M")
    
    with st.spinner("正在穿透东方财富与巨潮资讯服务器，全网扫盘中..."):
        try:
            fund_df = ak.fund_lof_spot_em()
        except Exception as e:
            st.error(f"数据源获取失败: {e}")
            fund_df = None

        if fund_df is not None and not fund_df.empty:
            overseas_keywords = ["纳斯", "标普", "原油", "油气", "商品", "互联", "中概", "日经", "德国", "法国", "印度", "越南", "亚洲", "全球", "海外"]
            premium_threshold = 2.0  # 商业实战溢价门槛
            
            count_target = 0
            
            # 专门用来一键复制的干净文案容器
            text_for_copy = f"🦅 搞钱小本本 · 盘中实时套利内参\n📡 扫盘时间：{current_time}\n"
            text_for_copy += "═" * 20 + "\n\n"
            
            # 网页前端可视化容器
            card_html_all = ""

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
                            
                            # 拼接群里转发的纯文本
                            text_for_copy += f"🔥 {count_target}. 【{name}】({code})\n"
                            text_for_copy += f"• 实时溢价率：{premium:.2f}%\n"
                            text_for_copy += f"• 场内现价：{price:.3f}元 | 成交额：{amount_wan:.2f}万元\n"
                            text_for_copy += f"• 场外申购：✅ {status_desc}\n\n"
                            
                            # 拼接网页上好看的暗夜卡片
                            card_html_all += f"""
                            <div class="fund-card">
                                <h3 style='color:#ff4b4b;margin-top:0;'>🔥 {count_target}. 【{name}】({code})</h3>
                                <p>📊 实时溢价率：<strong style='font-size:20px;color:#ff4b4b;'>{premium:.2f}%</strong></p>
                                <p>💰 场内现价：{price:.3f} 元 | 💸 成交额：{amount_wan:.2f} 万元</p>
                                <p>🟢 场外申购状态：<strong>{status_desc}</strong></p>
                            </div>
                            """
                    except:
                        continue

            if count_target == 0:
                st.info("⚖️ 盘中扫描完成：当前全市场套利品种情绪平稳，暂未出现符合门槛的疯狂品种。")
            else:
                text_for_copy += "═" * 20 + "\n💡 纪律：请在15:00前完成场外下单，注意防范冲击成本！"
                
                # 🍏 左右分栏：左边用来看精美卡片，右边留给梁总一秒复制文案发群
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### 🖥️ 实时视觉看板")
                    st.markdown(card_html_all, unsafe_allow_html=True)
                with col2:
                    st.markdown("### 📋 微信/飞书一键复制文案栏")
                    st.text_area("长按全选复制下方文本，直接轰炸社群：", value=text_for_copy, height=450)
