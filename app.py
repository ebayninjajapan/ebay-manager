import streamlit as st
import pandas as pd
import requests
import os
import re
import time
from datetime import datetime
import urllib.parse
from bs4 import BeautifulSoup

st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# ─────────────────────────────────────────
# 関数定義（インデントを正常化）
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in ["ID", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "確定レート"]:
            if col not in df.columns:
                df[col] = 0.0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        if "メモ" not in df.columns:
            df["メモ"] = ""
        df["ID"] = df["ID"].astype(int)
        return df
    return pd.DataFrame(columns=["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"])

# ─────────────────────────────────────────
# 定数とメイン処理
# ─────────────────────────────────────────
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]

current_rate = get_rate()
df = load_data()

# データの計算処理（エラーが出ないよう安全に）
if "確定レート" not in df.columns:
    df["確定レート"] = 0.0
df["使用レート"] = df["確定レート"].replace(0, current_rate)

# 画面表示
st.markdown(f"📦 eBay 仕入れ・利益管理システム | 💱 1 USD = {current_rate:.2f} JPY")

# タブ定義
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    st.write("在庫管理表")
    edited_df = st.data_editor(df, num_rows="dynamic")
    if st.button("💾 保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.rerun()

with tab4:
    st.download_button("CSVダウンロード", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")
