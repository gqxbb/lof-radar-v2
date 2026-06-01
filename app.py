import streamlit as st
import akshare as ak
import os
import datetime
from datetime import timezone, timedelta
import pandas as pd
import requests

# 强行忽略可能导致报错的海外代理
os.environ['NO_PROXY'] = 'eastmoney.com,sinajs.cn,feishu.cn'

# 🍏 宽屏实战排版
st.set_page_config(page_title="🦅 搞钱小本本 · LOF决战雷达", layout="wide")

# 梁总持有的真实 PDU 字符串钥匙
PUSHDEER_KEY = "PDU41743TMGmcUxFLSheqxKbOVZg6iqy8JH0i1q6a" 

# 注入高档深色系黑客风格 CSS 样式表
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #ECF0F1; }
    .stApp h1 { text-align: left; font-size: 30px; font-weight: bold; color: #FFFFFF; }
    .time-banner { 
        background: linear-gradient(135deg, #1E3A8A, #3B82F6); 
        padding: 15px; 
        border-radius: 8px; 
        margin-bottom: 20px; 
        border: 1px solid #60A5FA;
    }
    .remind-text { font-size: 16px; color: #FFFFFF; font-weight: bold; }
    .lof-card { 
        background-color: #1F242D; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 15px; 
        border-left: 5px solid #FF4B4B;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); 
    }
    .lof-card:hover {
        border-left: 5px solid #FF7676;
        background-color: #262C38;
        transition: 0.2s;
    }
    .lof-title { color: #FFFFFF; font-size: 18px; font-weight: bold; }
    .premium-text { color: #FF4B4B; font-size: 20px; font-weight: bold; }
    .stButton>button {
        background-color: #FF4B4B; color: white; width: 100%; 
        font-size: 22px; font-weight: bold; border-radius: 10px; height: 55px;
    }
    </style>
""", unsafe_allow_html=True)

# 严格锁定北京时间时区
SHA_TZ = timezone(timedelta(hours=8))
now = datetime.datetime.now(SHA_TZ)
now_time = now.strftime("%Y-%m-%d %H:%M:%S")

st.markdown(f"""
    <div class="time-banner">
        <div class="remind-text">⚡ 战术铁律：请于交易日【14:30】准时刷新，捕捉盲区最后一公里的疯狂价差！</div>
        <div style="font-size: 13px; color: #BFDBFE; margin-top: 3px;">当前北京时间：{now_time} | 网页服务已部署双数据源热备天线</div>
    </div>
""", unsafe_allow_html=True)

st.title("🦅 搞钱小本本 · LOF溢价盲区决战雷达")
st.markdown("<p style='color: #9CA3AF; margin-top:-10px;'>支持东财/新浪双路动态交叉流的 A 股全市场多维跨国扫盘引擎</p>", unsafe_allow_html=True)
st.write("")

# 核心过滤配置
overseas_keywords = ["纳斯", "标普", "原油", "油气", "商品", "互联", "中概", "日经", "德国", "法国", "印度", "越南", "亚洲", "全球", "海外"]
premium_threshold = 3.0  # 严格执行 3% 门槛

if st.button("🔄 立即暴力刷新全市场 LOF 溢价数据并同步推送"):
    with st.spinner("正在启动双弹夹扫描引擎，强制突防行情网中..."):
        
        fund_df = None
        source_name = "东方财富主干网"
        
        # 👑 【第一弹夹】：首先尝试读取东财实时行情
        try:
            fund_df = ak.fund_lof_spot_em()
            if fund_df is None or fund_df.empty:
                raise Exception("数据为空")
        except Exception as e:
            # 🚨 【自动换弹】：东财如果拔线拦截，瞬间无缝切换至新浪主干网保底！
            source_name = "新浪财经备用网"
            try:
                # 抓取新浪全市场基金实时行情
                sina_df = ak.fund_etf_category_sine()
                if sina_df is not None and not sina_df.empty:
                    # 统一字段清洗，无缝对齐东财格式
                    sina_df.rename(columns={'代码': '基金代码', '名称': '基金简称', '对应净值': '最新净值'}, inplace=True)
                    # 新浪盘中实时溢价计算
                    sina_df['现价'] = pd.to_numeric(sina_df['最新价'], errors='coerce')
                    sina_df['最新净值'] = pd.to_numeric(sina_df['最新净值'], errors='coerce')
                    sina_df['溢价率'] = (sina_df['现价'] - sina_df['最新净值']) / sina_df['最新净值'] * 100
                    fund_df = sina_df
            except Exception as sina_err:
                st.error(f"❌ 商业多路天线全部遭遇强力拦截，请稍后重试: {sina_err}")
                fund_df = None

        if fund_df is not None and not fund_df.empty:
            count_target = 0
            
            # 提示当前生效的数据通道，彰显量化系统的高级感
            st.success(f"⚡ 链路安全连通！当前由【{source_name}】提供盘中高可靠时序数据。")
            
            # 初始化一键复制文本框容器
            text_for_copy = f"🦅 搞钱小本本 · 盘中实时套利内参\n📡 扫盘时间：{now.strftime('%Y-%m-%d %H:%M')} (通道:{source_name})\n"
            text_for_copy += "═" * 20 + "\n\n"
            
            card_html_all = ""

            for index, row in fund_df.iterrows():
                if '基金代码' not in row or '基金简称' not in row:
                    continue
                code = str(row['基金代码']).replace("sh", "").replace("sz", "")
                name = row['基金简称']
                
                # 穿透过滤核心跨境品种
                is_overseas = any(keyword in name for keyword in overseas_keywords) or code.startswith("1611") or code.startswith("1649") or code.startswith("501")
                
                if is_overseas:
                    try:
                        premium = float(row['溢价率'])
                        if premium >= premium_threshold:
                            
                            # 优雅降级防护巨潮限流
                            try:
                                limit_info = ak.fund_open_format_xw()
                                matched_fund = limit_info[limit_info['基金代码'] == code]
                                status_desc = matched_fund.iloc[0]['申购状态'] if not matched_fund.empty else "开放申购"
                            except:
                                status_desc = "开放申购"

                            # 铁血过滤暂停申购的假肉票
                            if "暂停申购" in status_desc or "停申" in status_desc or status_desc == "暂停":
                                continue
                                
                            count_target += 1
                            price = float(row.get('现价', 0.0))
                            raw_amount = float(row.get('成交额', 0.0))
                            amount_wan = raw_amount if code.startswith("50") else raw_amount / 10000.0
                            
                            # 1. 纯文本拼接
                            text_for_copy += f"🔥 {count_target}. 【{name}】({code})\n"
                            text_for_copy += f"• 实时溢价率：{premium:.2f}%\n"
                            text_for_copy += f"• 场内现价：{price:.3f}元 | 成交额：{amount_wan:.2f}万元\n"
                            text_for_copy += f"• 场外状态：✅ {status_desc}\n\n"
                            
                            # 2. 前端卡片布局
                            warn_text = "⚠️ 流动性偏低，注意防范冲击成本！" if amount_wan < 200 else "🟢 成交活跃，属于优质套利标的！"
                            warn_color = "#FF4B4B" if amount_wan < 200 else "#10B981"
                            
                            card_html_all += f"""
                            <div class="lof-card">
                                <div class="lof-title">{count_target}. 【{name}】 ({code})</div>
                                <div style="margin-top: 8px;">
                                    <span class="premium-text">实时盘中溢价率：{premium:.2f}%</span>
                                </div>
                                <div style="margin-top: 8px; color: #9CA3AF; font-size: 14px;">
                                    • 场内现价：<b style="color: #FFFFFF;">{price:.3f} 元</b> &nbsp;&nbsp;|&nbsp;&nbsp; 
                                    当日成交额：<b style="color: #FFFFFF;">{amount_wan:.2f} 万元</b>
                                </div>
                                <div style="margin-top: 4px; color: #9CA3AF; font-size: 14px;">
                                    • 场外申购状态：<b style="color: #10B981;">{status_desc}</b>
                                </div>
                                <div style="margin-top: 6px; color: {warn_color}; font-size: 13px; font-weight: bold;">
                                    {warn_text}
                                </div>
                            </div>
                            """
                    except:
                        continue

            # 分栏布局展现
            col_left_panel, col_right_panel = st.columns(2)

            if count_target == 0:
                with col_left_panel:
                    st.info("⚖️ 盘中扫描完成：当前全市场实时溢价情绪平稳，暂未发现符合门槛（>=3%）的套利品种。")
                with col_right_panel:
                    text_for_copy += "📊 当前市场套利情绪平静，暂无达标品种，建议按兵不动。"
                    st.text_area("📋 微信/飞书一键复制文案栏（快照版）", value=text_for_copy, height=150)
            else:
                text_for_copy += "═" * 20 + "\n💡 纪律：请在15:00前完成场外下单，注意防范冲击成本！"
                
                with col_left_panel:
                    st.markdown(f"### 🖥️ 实时高溢价视觉看板 ({count_target} 只达标)")
                    st.markdown(card_html_all, unsafe_allow_html=True)
                    
                with col_right_panel:
                    st.markdown("### 📋 微信/飞书一键复制文案栏")
                    st.text_area("长按全选复制下方文本，直接轰炸社群：", value=text_for_copy, height=450)
                    
                    # 触发微信 PushDeer 推送
                    if PUSHDEER_KEY:
                        try:
                            push_title = f"🦅 发现 {count_target} 只高溢价套利标的！"
                            requests.get(f"https://api2.pushdeer.com/message/push?text={push_title}&desp={text_for_copy}&pushkey={PUSHDEER_KEY}")
                            st.success("🚀 PushDeer 微信端推手已同步离线空降！")
                        except:
                            pass
