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
# データ取得・ロード系関数
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
# 定数とUI設定
# ─────────────────────────────────────────
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]

current_rate = get_rate()

st.markdown('<p style="font-size:1.6rem; font-weight:800; color:#1A5C3A;">📦 eBay 仕入れ・利益管理システム</p>', unsafe_allow_html=True)
st.write(f"💱 現在のレート: 1 USD = {current_rate:.2f} JPY")

# ─────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────
df = load_data()

tab1, tab2 = st.tabs(["📋 在庫管理表", "その他"])

with tab1:
    edited_df = st.data_editor(df, num_rows="dynamic")
    if st.button("💾 保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("保存完了")
        st.rerun()

st.write("システム稼働中")

# 監視機能の関数を追記
def load_watch_list():
    if os.path.exists(WATCH_FILE):
        try:
            w = pd.read_csv(WATCH_FILE)
            for col in ["狙う仕入れ価格", "前回最安値", "eBay相場(ドル)"]:
                if col not in w.columns: w[col] = 0.0
                w[col] = pd.to_numeric(w[col], errors="coerce").fillna(0.0)
            return w
        except: pass
    return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_all=1&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = [int(s) for s in re.findall(r'\d+', soup.get_text().replace(',', '')) if int(s) >= 100]
        return min(prices) if prices else None
    except: return None

# タブに監視機能を追加
if "w_df" not in st.session_state: st.session_state.w_df = load_watch_list()

with st.expander("🔥 監視リスト"):
    if st.button("🔄 自動巡回"):
        for i, row in st.session_state.w_df.iterrows():
            p = check_yahoo_auctions_html(row["商品名"])
            if p: st.session_state.w_df.at[i, "前回最安値"] = p
        st.session_state.w_df.to_csv(WATCH_FILE, index=False)
        st.rerun()
    st.dataframe(st.session_state.w_df)
