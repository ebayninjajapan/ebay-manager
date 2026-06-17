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
    
df["使用レート"] = df["確定レート"].replace(0, current_rate)

df["純利益(円)"] = (
df["eBay相場(ドル)"] * 0.85 * df["使用レート"]
- df["仕入(円)"]
- df["発送サイズ"].map(SIZE_COSTS).fillna(2000)
).astype(int)
df["売上換算(円)"] = (df["売値(ドル)"] * df["使用レート"]).astype(int)

now_month = datetime.now().month
this_month = df[df["日付"].dt.month == now_month]
sold = this_month[this_month["ステータス"].isin(["販売済み", "発送済"])]

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
# タブ
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
"📋 在庫管理表", "🔍 利益計算ツール", "📥 新規仕入れ登録", "💾 データDL", "🔥 お気に入り監視"
])

# TAB 1
with tab1:
st.subheader("📋 在庫管理表")
col_f1, col_f2, col_f3 = st.columns([2, 2, 1])
with col_f1:
filter_status = st.selectbox("ステータスで絞り込み", ["すべて"] + STATUS_OPTIONS)
with col_f2:
filter_user = st.selectbox("担当者で絞り込み", ["すべて"] + USER_OPTIONS)
with col_f3:
search_word = st.text_input("商品名で検索")
df_show = df.copy()
if filter_status != "すべて":
df_show = df_show[df_show["ステータス"] == filter_status]
if filter_user != "すべて":
df_show = df_show[df_show["担当者"] == filter_user]
if search_word:
df_show = df_show[df_show["商品名"].str.contains(search_word, na=False)]

if not df_show.empty and "日付" in df_show.columns:
df_show["日付"] = df_show["日付"].dt.strftime("%Y-%m-%d")

df_show.insert(0, "削除", False)
base_columns = ["ID", "日付", "担当者", "商品名", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "ステータス", "発送サイズ", "確定レート", "メモ"]

edited_df = st.data_editor(
df_show,
column_config={
"削除": st.column_config.CheckboxColumn("削除", width="small"),
"ID": st.column_config.NumberColumn("ID", disabled=True, format="%d"),
"ステータス": st.column_config.SelectboxColumn(options=STATUS_OPTIONS, required=True),
"発送サイズ": st.column_config.SelectboxColumn(options=SIZE_OPTIONS),
"担当者": st.column_config.SelectboxColumn(options=USER_OPTIONS),
},
width="stretch", hide_index=True, num_rows="dynamic", key="main_editor"
)

if st.button("💾 変更を保存", type="primary"):
saved_edited = edited_df[edited_df["削除"] == False].copy()
new_rows_list = []
updated_ids = set()

for _, row in saved_edited.iterrows():
pid = row.get("ID", 0)
if pd.isna(pid) or pid == 0 or int(pid) not in df["ID"].values:
next_id = int(df["ID"].max() + 1) if not df.empty else 1
while next_id in updated_ids: next_id += 1
row["ID"] = next_id
row["日付"] = datetime.now().strftime("%Y-%m-%d") if pd.isna(row.get("日付")) else row["日付"]
new_dict = {col: row.get(col, "") for col in base_columns}
if new_dict["ステータス"] in ["販売済み", "発送済"] and (pd.isna(new_dict["確定レート"]) or new_dict["確定レート"] == 0):
new_dict["確定レート"] = current_rate
new_rows_list.append(new_dict)
updated_ids.add(next_id)
else:
pid = int(pid)
updated_ids.add(pid)
if row["ステータス"] in ["販売済み", "発送済"] and row["確定レート"] == 0:
row["確定レート"] = current_rate
for col in base_columns:
if col in row: df.loc[df["ID"] == pid, col] = row[col]

visible_ids = set(df_show["ID"].dropna().astype(int).values)
deleted_ids = visible_ids - updated_ids
if deleted_ids: df = df[~df["ID"].isin(deleted_ids)]
# 新規行の追加処理（new_rows_list がある場合）
        if new_rows_list:
            df = pd.concat([df, pd.DataFrame(new_rows_list)], ignore_index=True)
        
        # 最終的な保存
        df.to_csv(DB_FILE, index=False)
        st.success("保存しました！")
        st.rerun()
$('lEbaySold').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(currentEn)+'&LH_Sold=1&LH_Complete=1'; $('lEbaySold').classList.remove('off');
    } else { $('lEbay').classList.add('off'); $('lEbaySold').classList.add('off'); }
  }

  function calc() {
    const rate = num('exchangeRate'); const cost = num('costPrice'); const price = num('itemPrice');
    const revenue = price * rate;
    const expense = cost + (revenue * 0.15) + 2000; // 手数料15%+送料等2000円想定
    const profit = revenue - expense;
    const margin = revenue > 0 ? ((profit / revenue) * 100).toFixed(1) : 0;
    
    $('pProfit').textContent = Math.round(profit).toLocaleString() + '円';
    $('pProfit').className = 'val ' + (profit >= 0 ? 'pos' : 'neg');
    $('pRate').textContent = '利益率 ' + margin + '%';
    $('pRevenue').textContent = Math.round(revenue).toLocaleString() + '円';
    $('pExpense').textContent = Math.round(expense).toLocaleString() + '円';
  }

  $('jaInput').oninput = (e) => { currentJa = e.target.value; $('gTransJa').href='https://translate.google.co.jp/?hl=ja&sl=ja&tl=en&text='+encodeURIComponent(currentJa); updateButtons(); };
  $('enInput').oninput = (e) => { currentEn = e.target.value; $('gTransEn').href='https://translate.google.co.jp/?hl=en&sl=en&tl=ja&text='+encodeURIComponent(currentEn); updateButtons(); };
  ['exchangeRate', 'costPrice', 'itemPrice'].forEach(id => $(id).oninput = calc);
})();
</script>"""
    st.components.v1.html(html_calc_template.replace("__CURRENT_RATE__", str(round(current_rate, 2))), height=650)

# ─────────────────────────────────────────
# TAB 3, 4, 5
# ─────────────────────────────────────────
with tab3:
    st.subheader("📥 新規仕入れ登録")
    with st.form("new_item_form"):
        col1, col2 = st.columns(2)
        n_name = col1.text_input("商品名")
        n_user = col2.selectbox("担当者", USER_OPTIONS)
        n_cost = col1.number_input("仕入金額(円)", 0)
        n_size = col2.selectbox("発送サイズ", SIZE_OPTIONS)
        if st.form_submit_button("登録"):
            new_row = pd.DataFrame([{"ID": df["ID"].max()+1 if not df.empty else 1, "商品名": n_name, "担当者": n_user, "仕入(円)": n_cost, "ステータス": "掲載前", "発送サイズ": n_size, "日付": datetime.now().strftime("%Y-%m-%d")}])
            pd.concat([df, new_row]).to_csv(DB_FILE, index=False)
            st.success("登録完了！")
            st.rerun()

with tab4:
    st.subheader("💾 データダウンロード")
    st.download_button("CSVとして保存", df.to_csv(index=False).encode('utf-8-sig'), "stock_list.csv")

with tab5:
    st.subheader("🔥 お気に入り監視")
    st.dataframe(st.session_state.w_df, use_container_width=True)
