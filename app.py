import streamlit as st
import pandas as pd
import requests
import os
import re
import time
import urllib.parse
from datetime import datetime
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

# --- 設定・定数 ---
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")
DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# --- 定数定義 ---
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]
base_columns = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]

# --- 関数 ---
@st.cache_data(ttl=300)
def get_rate():
    try: return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except: return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        for col in ["ID", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "確定レート"]:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        return df
    return pd.DataFrame(columns=base_columns)

def load_watch_list():
    if os.path.exists(WATCH_FILE):
        w = pd.read_csv(WATCH_FILE)
        return w.loc[:, ~w.columns.duplicated()]
    return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        prices = [int(re.sub(r'[^\d]', '', p.text)) for p in soup.find_all(class_=re.compile("Product__priceValue")) if re.sub(r'[^\d]', '', p.text)]
        return min(prices) if prices else None
    except: return None

# --- メインロジック ---
current_rate = get_rate()
df = load_data()
if "w_df" not in st.session_state: st.session_state.w_df = load_watch_list()

st.title("📦 eBay 仕入れ管理システム")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    # 既存の在庫管理表ロジック
    df_show = df.copy()
    edited_df = st.data_editor(df_show, num_rows="dynamic", key="main_editor")
    if st.button("💾 変更を保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.rerun()

with tab2:
    # 利益計算HTML埋め込み
    html_template = """...ここに前回送ってもらったHTMLを貼り付け..."""
    components.html(html_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}"), height=700)

with tab3:
    # 新規登録ロジック
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("商品名")
        if st.form_submit_button("登録"):
            # ここに登録ロジック
            st.rerun()

with tab4:
    st.download_button("CSV DL", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")

with tab5:
    # 監視リストの長いロジック
   
