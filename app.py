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

# ページ設定
st.set_page_config(layout="wide", page_title="eBay 仕入れ管理", page_icon="📦")

DB_FILE = "l_database.csv"
WATCH_FILE = "watch_list.csv"

# --- 定数・関数 ---
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]
base_columns = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]

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
    search_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
    try:
        response = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        prices = [int(re.sub(r'[^\d]', '', p.text)) for p in soup.find_all(class_=re.compile("Product__priceValue")) if re.sub(r'[^\d]', '', p.text)]
        return min(prices) if prices else None
    except: return None

# --- メインロジック ---
current_rate = get_rate()
df = load_data()
if "w_df" not in st.session_state: st.session_state.w_df = load_watch_list()

st.markdown(f"### 📦 eBay 仕入れ・利益管理システム (Rate: {current_rate:.2f})")
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 在庫", "🔍 計算", "📥 登録", "💾 DL", "🔥 監視"])

with tab1:
    # (在庫管理表ロジックをここに配置)
    edited_df = st.data_editor(df, num_rows="dynamic", key="main_editor")
    if st.button("💾 変更を保存"):
        edited_df.to_csv(DB_FILE, index=False)
        st.rerun()

with tab2:
    html_calc_template = """with tab2:
    st.subheader("🔍 eBay利益計算・ハイブリッドツール")
    
    # テンプレートを三重引用符で定義
    html_calc_template = """
    <!DOCTYPE html>
    <html lang="ja">
    <head><meta charset="UTF-8">
    <style>
        :root{--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;--dim:#9ca89e;--accent:#B79740;--teal:#1A5C3A;--teal2:#2D7A4F;--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;}
        *{box-sizing:border-box;margin:0;padding:0;}
        body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;background:var(--bg);color:var(--text);padding:10px 12px 280px;}
        .sec{background:var(--card);margin:8px 0;border-radius:var(--r);padding:14px;border:1px solid var(--border);}
        .lbl{display:block;font-size:11px;font-weight:600;color:var(--sub);margin-bottom:4px;}
        input,select{width:100%;padding:10px 11px;border:1px solid var(--iborder);border-radius:var(--rs);font-size:15px;background:var(--ibg);color:var(--text);}
        .mb{margin-bottom:11px;}
        .trans-box{display:flex;gap:6px;align-items:stretch;}
        .trans{flex:1;background:rgba(26,92,58,.06);padding:10px;border-radius:var(--rs);font-size:13px;min-height:36px;display:flex;align-items:center;color:var(--teal);font-weight:700;word-break:break-all;}
        .btn-gtrans{padding:0 12px;background:#4285F4;color:#fff;border:none;border-radius:var(--rs);font-size:11px;font-weight:bold;cursor:pointer;display:flex;align-items:center;text-decoration:none;}
        .links-title{font-size:11px;font-weight:700;color:var(--sub);margin:14px 0 6px;}
        .links-row{display:flex;gap:8px;margin-bottom:10px;}
        .btn-search{flex:1;text-align:center;padding:11px 5px;border-radius:var(--rs);text-decoration:none;font-size:12px;font-weight:800;color:#fff;display:block;box-shadow:0 2px 4px rgba(0,0,0,.08);}
        .btn-search.mercari{background:linear-gradient(135deg,#e32b2b,#b51212);}
        .btn-search.yahoo{background:linear-gradient(135deg,#ffaa00,#cc8800);color:#1a1a1a;}
        .btn-search.ebay-live{background:linear-gradient(135deg,#0064d2,#0050a5);}
        .btn-search.ebay-sold{background:linear-gradient(135deg,#2d7a4f,#1a5c3a);}
        .btn-search.off{opacity:.3;pointer-events:none;background:#ccc !important;color:#666;}
        .panel{position:fixed;bottom:0;left:0;right:0;background:#fafbf9;border-top:1px solid var(--border);padding:11px 14px;box-shadow:0 -4px 12px rgba(0,0,0,.05);z-index:99;}
        .profits{display:flex;margin-bottom:7px;border-bottom:1px solid var(--border);padding-bottom:8px;}
        .pcol{flex:1;text-align:center;}
        .pcol .val{font-size:22px;font-weight:900;}
        .pos{color:var(--pp);}.neg{color:var(--pn);}
        .summary{display:flex;justify-content:space-around;font-size:11px;color:var(--sub);}
        .split-grid{display:flex;gap:12px;}
        .split-col{flex:1;}
    </style>
    </head>
    <body>
        <div class="split-grid">...</div> 
        <script>
            /* ここに送ってくれた script の中身を全て貼り付け */
            (function(){ ... })();
        </script>
    </body>
    </html>
    """
    
    # 最後にレートを置換して表示
    st.html(html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}"))"""
    components.html(html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}"), height=700)

with tab3:
    # (新規登録ロジック)
    with st.form("add_form"):
        # ... (第5回でいただいた登録ロジック) ...
        if st.form_submit_button("✅ 登録"): st.rerun()

with tab4:
    st.download_button("📥 CSVダウンロード", df.to_csv(index=False).encode('utf-8-sig'), "data.csv")

with tab5:
    # (今回送っていただいた長い監視ロジックをここに貼り付け)
    # ... (監視リストの詳細ロジック) ...
