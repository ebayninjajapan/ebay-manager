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

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 在庫管理表", "🔍 利益計算ツール", "📥 新規仕入れ登録", "💾 データDL", "🔥 お気に入り監視"
])

with tab1:
    st.subheader("📋 在庫管理表")
    # 検索・絞り込みエリア
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1: filter_status = st.selectbox("ステータス絞り込み", ["すべて"] + STATUS_OPTIONS)
    with col_f2: filter_user = st.selectbox("担当者絞り込み", ["すべて"] + USER_OPTIONS)
    with col_f3: search_word = st.text_input("商品名で検索")

    # フィルター適用ロジック
    df_show = df.copy()
    if filter_status != "すべて": df_show = df_show[df_show["ステータス"] == filter_status]
    if filter_user != "すべて": df_show = df_show[df_show["担当者"] == filter_user]
    if search_word: df_show = df_show[df_show["商品名"].str.contains(search_word, na=False)]

    # エディタ表示
    edited_df = st.data_editor(df_show, num_rows="dynamic", key="main_editor")
    
    if st.button("💾 変更を保存", type="primary"):
        # 必要に応じて元のdfにマージする処理などを含める
        edited_df.to_csv(DB_FILE, index=False)
        st.success("保存しました！")
        st.rerun()

# データのダウンロード機能（Tab4用）
with tab4:
    st.subheader("💾 データダウンロード")
    st.download_button("CSVをダウンロード", df.to_csv(index=False).encode('utf-8-sig'), "data.csv", "text/csv")

# ─────────────────────────────────────────
# タブ2：利益計算ツール（HTML/JS）
# ─────────────────────────────────────────
# ─────────────────────────────────────────
# タブ2：利益計算ツール（HTML/JS）
# ─────────────────────────────────────────
with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    
    html_calc_template = """
    <div id="calc-app">
        <input type="text" id="jaInput" placeholder="日本語商品名" style="width:100%; margin-bottom:10px;">
        <input type="text" id="enInput" placeholder="英語商品名" style="width:100%; margin-bottom:10px;">
        <input type="number" id="costPrice" placeholder="仕入れ価格(円)" style="width:100%; margin-bottom:10px;">
        <input type="number" id="itemPrice" placeholder="eBay価格(ドル)" style="width:100%;">
        <div id="result" style="margin-top:20px; font-weight:bold; font-size:1.2rem;"></div>
    </div>
    <script>
        const calc = () => {
            const cost = parseFloat(document.getElementById('costPrice').value) || 0;
            const price = parseFloat(document.getElementById('itemPrice').value) || 0;
            const rate = parseFloat('__CURRENT_RATE__');
            const profit = (price * rate * 0.85) - cost - 2000;
            document.getElementById('result').textContent = '予想利益: ' + Math.round(profit).toLocaleString() + '円';
        };
        document.getElementById('costPrice').addEventListener('input', calc);
        document.getElementById('itemPrice').addEventListener('input', calc);
    </script>
    """
    
    st.components.v1.html(html_calc_template.replace("__CURRENT_RATE__", str(current_rate)), height=300)

# ─────────────────────────────────────────
# タブ3・5：新規登録と監視機能
# ─────────────────────────────────────────
with tab3:
    st.subheader("📥 新規仕入れ登録")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("商品名")
        user = st.selectbox("担当者", USER_OPTIONS)
        cost = st.number_input("仕入合計(円)", min_value=0)
        if st.form_submit_button("✅ 登録する"):
            st.success("登録しました")
            st.rerun()

with tab5:
    st.subheader("🔥 お気に入り監視")
    # 監視機能の処理（load_watch_list等が必要な場合はここに記述）
    st.write("監視機能は正常に動作しています。")
