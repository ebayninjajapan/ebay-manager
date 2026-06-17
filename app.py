import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime

# 設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
DB_FILE = "l_database.csv"

# レート取得
@st.cache_data(ttl=300)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

# データ読み込み
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "日付", "商品名", "仕入(円)", "ステータス"])

# 初期化
current_rate = get_rate()
df = load_data()

# 画面表示
st.title("📦 eBay 仕入れ管理システム")
st.metric("1 USD", f"{current_rate:.2f} JPY")

# タブ作成
tab1, tab2 = st.tabs(["📋 在庫管理表", "🔍 利益計算ツール"])

with tab1:
    st.subheader("現在の在庫")
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("利益計算")
    cost = st.number_input("仕入れ価格(円)", value=0)
    price = st.number_input("eBay販売価格(ドル)", value=0.0)
    profit = (price * current_rate * 0.85) - cost - 2000
    st.write(f"予想利益: {int(profit):,} 円")
