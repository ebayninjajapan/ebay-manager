import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

DB_FILE = "l_database.csv"
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]

@st.cache_data(ttl=300)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
    except:
        return 155.0

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"])

current_rate = get_rate()
df = load_data()
base_columns = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]

st.title("📦 eBay 仕入れ管理システム")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫管理表", "🔍 利益計算ツール", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    edited_df = st.data_editor(df, num_rows="dynamic", key="main_editor")
    if st.button("💾 変更を保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.success("✅ 保存しました")
        st.rerun()

with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    # ここに以前のHTMLテンプレートを読み込みます
    html_calc_template = """(省略: 以前のHTML/JSコードをここに配置)"""
    components.html(html_calc_template.replace("__CURRENT_RATE__", str(round(current_rate, 2))), height=700)

with tab3:
    st.subheader("📥 新規仕入れ登録")
    with st.form("new_item"):
        name = st.text_input("商品名")
        cost = st.number_input("仕入(円)", 0)
        if st.form_submit_button("登録"):
            new_row = pd.DataFrame([{"ID": df["ID"].max()+1 if not df.empty else 1, "商品名": name, "仕入(円)": cost, "日付": datetime.now().strftime("%Y-%m-%d")}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.rerun()

with tab4:
    st.download_button("CSVダウンロード", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")

with tab5:
    st.write("監視リスト機能")
