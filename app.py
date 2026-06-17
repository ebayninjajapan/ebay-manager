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

def load_watch_list():
    if os.path.exists(WATCH_FILE):
        try:
            w = pd.read_csv(WATCH_FILE)
            if "eBay最安値(ドル)" in w.columns and "eBay相場(ドル)" not in w.columns:
                w = w.rename(columns={"eBay最安値(ドル)": "eBay相場(ドル)"})
            for col in ["狙う仕入れ価格", "前回最安値", "eBay相場(ドル)"]:
                if col not in w.columns:
                    w[col] = 0.0
                w[col] = pd.to_numeric(w[col], errors="coerce").fillna(0.0)
            if "状態" not in w.columns:
                w["状態"] = "🆕 未チェック"
            return w
        except:
            pass
    return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"])

def check_yahoo_auctions_html(keyword):
    encoded_kw = urllib.parse.quote(keyword)
    search_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&n=50"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(search_url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        prices = [int(re.sub(r'[^\d]', '', p.text)) for p in soup.find_all(class_=re.compile("Price__value")) if re.sub(r'[^\d]', '', p.text)]
        return min(prices) if prices else None
    except:
        return None

# ─────────────────────────────────────────
# 定数定義
# ─────────────────────────────────────────
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]
# ─────────────────────────────────────────
# データ前処理と計算
# ─────────────────────────────────────────
df = load_data()
df["日付"] = pd.to_datetime(df["日付"], errors="coerce")
df["使用レート"] = df["確定レート"].replace(0, current_rate)

# 純利益の計算
df["純利益(円)"] = (
    df["eBay相場(ドル)"] * 0.85 * df["使用レート"]
    - df["仕入(円)"]
    - df["発送サイズ"].map(SIZE_COSTS).fillna(2000)
).astype(int)

# 売上換算の計算
df["売上換算(円)"] = (df["売値(ドル)"] * df["使用レート"]).astype(int)

# 今月の集計データ
now_month = datetime.now().month
this_month = df[df["日付"].dt.month == now_month]
sold = this_month[this_month["ステータス"].isin(["販売済み", "発送済"])]

# お気に入り監視リストの初期化
if "w_df" not in st.session_state:
    st.session_state.w_df = load_watch_list()

# ─────────────────────────────────────────
# ダッシュボード
# ─────────────────────────────────────────
st.subheader("📈 今月の実績")
m1, m2, m3, m4 = st.columns(4)
m1.metric("今月 仕入れ合計", f"¥{this_month['仕入(円)'].sum():,.0f}")
m2.metric("今月 売上合計", f"¥{sold['売値(ドル)'].sum() * current_rate:,.0f}")
m3.metric("今月 確定利益", f"¥{sold['純利益(円)'].sum():,.0f}")
m4.metric("在庫件数（掲載中）", len(df[df["ステータス"] == "掲載中"]))

st.divider()

# ─────────────────────────────────────────
# タブの定義
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 在庫管理表", "🔍 利益計算ツール", "📥 新規仕入れ登録", "💾 データDL", "🔥 お気に入り監視"
])
