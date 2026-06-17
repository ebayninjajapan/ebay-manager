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

SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]
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
# データ取得・ロード
# ─────────────────────────────────────────
@st.cache_data(ttl=300)
def get_rate():
    try:
        return float(requests.get("https://open.er-api.com/v6/latest/USD", timeout=3).json()["rates"]["JPY"])
        except:
            return 155.0
            def load_data():
                if os.path.exists(DB_FILE)
                df = pd.read_csv(DB_FILE)
                for col in ["ID", "仕入(円)", "eBay相場(ドル)", "売値(ドル)", "確定レート"]:
                    if col not in df.columns:
                        df[col] = 0.0
                        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
                        if "メモ" not in df.columns:
                            df["メモ"] = ""
                            df["ID"] = df["ID"].astype(int)
return df
return pd.DataFrame(columns=[
"ID", "日付", "担当者", "商品名", "仕入(円)",
"eBay相場(ドル)", "売値(ドル)", "ステータス",
"発送サイズ", "確定レート", "メモ"
])

def load_watch_list():
if os.path.exists(WATCH_FILE):
try:
w = pd.read_csv(WATCH_FILE)
# 列名の重複防止・リネーム処理
if "eBay最安値(ドル)" in w.columns and "eBay相場(ドル)" not in w.columns:
w = w.rename(columns={"eBay最安値(ドル)": "eBay相場(ドル)"})
elif "eBay最安値(ドル)" in w.columns and "eBay相場(ドル)" in w.columns:
w = w.drop(columns=["eBay最安値(ドル)"])

# 必要な列が確実に1つずつ存在するように調整
for col in ["狙う仕入れ価格", "前回最安値", "eBay相場(ドル)"]:
if col not in w.columns:
w[col] = 0.0
w[col] = pd.to_numeric(w[col], errors="coerce").fillna(0.0)
if "状態" not in w.columns:
w["状態"] = "🆕 未チェック"

# 重複列を完全に排除して必要な列のみを抽出
w = w.loc[:, ~w.columns.duplicated()]
return w[["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"]]
except:
pass
return pd.DataFrame(columns=["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"])


def check_yahoo_auctions_html(keyword):
encoded_kw = urllib.parse.quote(keyword)
search_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&is_all=1&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"

headers = {
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
"Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

try:
response = requests.get(search_url, headers=headers, timeout=10)
if response.status_code == 200:
soup = BeautifulSoup(response.text, 'html.parser')
price_elements = soup.find_all(class_=re.compile("Product__priceValue"))

prices = []
for elem in price_elements:
text = elem.get_text()
clean_text = text.replace(',', '').replace('円', '').strip()
nums = [int(s) for s in re.findall(r'\d+', clean_text)]
for num in nums:
if num >= 100:
prices.append(num)
if prices:
return min(prices)
except:
pass
return None

# ─────────────────────────────────────────
# 定数
# ─────────────────────────────────────────
SIZE_COSTS = {"大(カメラなど)": 5000, "中(カメラなど)": 3000, "小": 1500, "極小": 800}
STATUS_OPTIONS = ["掲載前", "掲載中", "販売済み", "発送済"]
SIZE_OPTIONS = ["大(カメラなど)", "中(カメラなど)", "小", "極小"]
USER_OPTIONS = ["自分", "悠太郎", "その他"]

# ─────────────────────────────────────────
# ヘッダー
# ─────────────────────────────────────────
current_rate = get_rate()

st.markdown("""
<style>
    .main-header {font-size:1.6rem; font-weight:800; color:#1A5C3A;}
    .rate-badge {
        display:inline-block; background:#f0f9f3; border:1px solid #b0d8bc;
        color:#1A5C3A; font-weight:700; border-radius:8px; padding:4px 14px; font-size:0.95rem;
    }
    [data-testid="stMetricValue"] {font-size:1.5rem !important; font-weight:800;}
</style>
""", unsafe_allow_html=True)

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
st.markdown('<p class="main-header">📦 eBay 仕入れ・利益管理システム</p>', unsafe_allow_html=True)
with col_h2:
st.markdown(f'<p style="text-align:right;padding-top:12px"><span class="rate-badge">💱 1 USD = {current_rate:.2f} JPY</span></p>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# データ前処理と計算
# ─────────────────────────────────────────
df = load_data()
df["日付"] = pd.to_datetime(df["日付"], errors="coerce")

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
if new_rows_list: df = pd.concat([df, pd.DataFrame(new_rows_list)], ignore_index=True)

df[base_columns].to_csv(DB_FILE, index=False)
st.success("✅ 変更を保存しました！")
st.rerun()

# TAB 2
with tab2:
st.subheader("🔍 eBay利益計算・ハイブリッドツール")
html_calc_template = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="UTF-8">
<style>
:root{
--bg:#fff;--card:#fff;--border:rgba(26,59,40,.09);--text:#1a1a1a;--sub:#5a6b5e;
--dim:#9ca89e;--accent:#B79740;--teal:#1A5C3A;--teal2:#2D7A4F;
--pp:#1A7A42;--pn:#C62828;--ibg:#F5F7F5;--iborder:rgba(26,59,40,.15);--r:14px;--rs:8px;
}
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
</style></head>
<body>
<div class="split-grid">
  <div class="sec split-col" style="border-top:4px solid #e32b2b;">
    <div class="mb"><label class="lbl">🇯🇵 日本語の商品名を入力</label><input id="jaInput" type="text" placeholder="例：デジモン ぬいぐるみ"></div>
    <div class="mb">
      <label class="lbl">🇺🇸 自動英語訳</label>
      <div class="trans-box">
        <div class="trans" id="jaToEnResult">英語に翻訳されます</div>
        <a href="#" id="gTransJa" class="btn-gtrans" target="_blank">G翻訳↗</a>
      </div>
    </div>
  </div>
  <div class="sec split-col" style="border-top:4px solid #0064d2;">
    <div class="mb"><label class="lbl">🇺🇸 英語の商品名・型番を入力</label><input id="enInput" type="text" placeholder="例：Nikon F3 Camera"></div>
    <div class="mb">
      <label class="lbl">🇯🇵 自動日本語訳</label>
      <div class="trans-box">
        <div class="trans" id="enToJaResult">日本語に翻訳されます</div>
        <a href="#" id="gTransEn" class="btn-gtrans" target="_blank">G翻訳↗</a>
      </div>
    </div>
  </div>
</div>
<div class="sec" style="background:#f9fbf9;">
  <div class="links-title" style="margin-top:0;">🇯🇵 国内仕入れ元を検索（日本語ワード連動）</div>
  <div class="links-row">
    <a href="#" class="btn-search mercari off" id="lMercari" target="_blank">🔴 メルカリで検索</a>
    <a href="#" class="btn-search yahoo off" id="lYahoo" target="_blank">🟡 ヤフオクで検索</a>
  </div>
  <div class="links-title">🇺🇸 海外eBay相場を検索（英語ワード連動）</div>
  <div class="links-row">
    <a href="#" class="btn-search ebay-live off" id="lEbay" target="_blank">🔵 eBay (販売中)</a>
    <a href="#" class="btn-search ebay-sold off" id="lEbaySold" target="_blank">🟢 eBay (売れ済/Sold)</a>
  </div>
</div>
<div class="sec">
  <div class="mb"><label class="lbl">為替レート (1ドルあたり)</label><input id="exchangeRate" type="text" value="__CURRENT_RATE__"></div>
  <div class="mb"><label class="lbl">仕入れ価格（円）</label><input id="costPrice" type="text" value="0"></div>
  <div class="mb"><label class="lbl">eBay 販売価格 (ドル入力)</label><input id="itemPrice" type="text" value="0"></div>
</div>
<div class="panel">
  <div class="profits">
    <div class="pcol"><div class="lbl">最終利益</div><div class="val pos" id="pProfit">0円</div><div id="pRate" style="font-size:11px;">利益率 0%</div></div>
  </div>
  <div class="summary"><span>売上: <strong id="pRevenue">0円</strong></span><span>経費: <strong id="pExpense">0円</strong></span></div>
</div>
<script>
(function(){
  const $=id=>document.getElementById(id);
  const num=id=>parseFloat(($(id).value||'').replace(/,/g,''))||0;
  let currentJa = ''; let currentEn = '';
  function updateButtons() {
    if(currentJa) {
      $('lMercari').href='https://jp.mercari.com/search?keyword='+encodeURIComponent(currentJa); $('lMercari').classList.remove('off');
      $('lYahoo').href='https://auctions.yahoo.co.jp/search/search?p='+encodeURIComponent(currentJa); $('lYahoo').classList.remove('off');
    } else { $('lMercari').classList.add('off'); $('lYahoo').classList.add('off'); }
    if(currentEn) {
      $('lEbay').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(currentEn); $('lEbay').classList.remove('off');
      $('lEbaySold').href='https://www.ebay.com/sch/i.html?_nkw='+encodeURIComponent(currentEn)+'&LH_Sold=1&LH_Complete=1'; $('lEbaySold').classList.remove('off');
    } else { $('lEbay').classList.add('off'); $('lEbaySold').classList.add('off'); }
  }
  $('jaInput').addEventListener('input', function(){
    const val = this.value.trim(); $('enInput').value = ''; 
    if(!val) { $('jaToEnResult').textContent = '英語に翻訳されます'; $('gTransJa').href = '#'; currentJa = ''; currentEn = ''; updateButtons(); return; }
    currentJa = val; $('gTransJa').href = 'https://translate.google.com/?sl=ja&tl=en&text=' + encodeURIComponent(val);
    setTimeout(async()=>{
      if($('jaInput').value.trim() !== val) return;
      try {
        const r = await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(val)+'&langpair=ja|en');
        const d = await r.json();
        if(d.responseData && d.responseData.translatedText) {
          currentEn = d.responseData.translatedText; $('jaToEnResult').textContent = currentEn; updateButtons(); calc();
        }
      } catch(e){}
    }, 400);
  });
  $('enInput').addEventListener('input', function(){
    const val = this.value.trim(); $('jaInput').value = ''; 
    if(!val) { $('enToJaResult').textContent = '日本語に翻訳されます'; $('gTransEn').href = '#'; currentJa = ''; currentEn = ''; updateButtons(); return; }
    currentEn = val; $('gTransEn').href = 'https://translate.google.com/?sl=en&tl=ja&text=' + encodeURIComponent(val);
    setTimeout(async()=>{
      if($('enInput').value.trim() !== val) return;
      try {
        const r = await fetch('https://api.mymemory.translated.net/get?q='+encodeURIComponent(val)+'&langpair=en|ja');
        const d = await r.json();
        if(d.responseData && d.responseData.translatedText) {
          let transText = d.responseData.translatedText;
          if (transText.toLowerCase() === val.toLowerCase()) { currentJa = val; $('enToJaResult').textContent = "⚠️直訳不可 (G翻訳ボタンをお試しください)"; }
          else { currentJa = transText; $('enToJaResult').textContent = currentJa; }
          updateButtons(); calc();
        }
      } catch(e){}
    }, 400);
  });
  function calc(){
    const rate=num('exchangeRate'), cost=num('costPrice'), item=num('itemPrice'); if(!rate)return;
    const rev=item*rate; const expense=cost+(rev*0.15); const profit=rev-expense;
    $('pProfit').textContent=Math.round(profit).toLocaleString()+'円';
    $('pProfit').className='val '+(profit>=0?'pos':'neg');
    $('pRate').textContent='利益率 '+(rev>0?(profit/rev*100).toFixed(1):0)+'%';
    $('pRevenue').textContent=Math.round(rev).toLocaleString()+'円';
    $('pExpense').textContent=Math.round(expense).toLocaleString()+'円';
  }
  ['exchangeRate','costPrice','itemPrice'].forEach(id=>$(id).addEventListener('input',calc));
})();
</script>
</body></html>"""
html_calc = html_calc_template.replace("__CURRENT_RATE__", f"{current_rate:.2f}")
st.html(html_calc)

# TAB 3
with tab3:
st.subheader("📥 新規仕入れ登録")
with st.form("add_form", clear_on_submit=True):
name = st.text_input("商品名 *")
user = st.selectbox("担当者 *", USER_OPTIONS)
cost = st.number_input("仕入合計（円）", min_value=0, step=100)
size = st.selectbox("発送サイズ", SIZE_OPTIONS)
status = st.selectbox("初期ステータス", STATUS_OPTIONS)
submitted = st.form_submit_button("✅ 登録する")
if submitted and name.strip():
next_id = int(df["ID"].max() + 1) if not df.empty else 1
new_row = pd.DataFrame([{
"ID": next_id, "日付": datetime.now().strftime("%Y-%m-%d"), "担当者": user,
"商品名": name.strip(), "仕入(円)": cost, "eBay相場(ドル)": 0, "売値(ドル)": 0,
"発送サイズ": size, "ステータス": status, "確定レート": 0, "メモ": ""
}])
pd.concat([df[base_columns], new_row], ignore_index=True).to_csv(DB_FILE, index=False)
st.success("登録しました！")
st.rerun()

# TAB 4
with tab4:
st.subheader("💾 データダウンロード")
st.download_button(
label="📥 管理データをCSVでダウンロード",
data=df.to_csv(index=False, encoding="utf-8-sig"),
file_name="ebay_data.csv", mime="text/csv", width="stretch"
)

# TAB 5
with tab5:
st.subheader("🔥 国内仕入れ元・自動新着監視")
with st.expander("➕ 新しい仕入れ候補・キーワードを登録する", expanded=False):
with st.form("add_watch_form", clear_on_submit=True):
w_name = st.text_input("仕入れたい商品名・キーワード（例：Nikon F3 本体）")
w_target_price = st.number_input("狙う仕入れ上限価格（円）", min_value=0, step=1000)
w_submitted = st.form_submit_button("➕ 監視リストに追加")
if w_submitted and w_name.strip():
new_w_row = pd.DataFrame([{
"商品名": w_name.strip(), "狙う仕入れ価格": w_target_price, "前回最安値": 0.0, "eBay相場(ドル)": 0.0, "状態": "🆕 未チェック"
}])
st.session_state.w_df = pd.concat([st.session_state.w_df, new_w_row], ignore_index=True)
st.session_state.w_df.to_csv(WATCH_FILE, index=False)
st.success(f"「{w_name}」を監視リストに登録しました！")
st.rerun()

if not st.session_state.w_df.empty:
col_btn1, col_btn2 = st.columns([3, 2])
with col_btn1:
if st.button("🔄 登録キーワードを今すぐ自動巡回（ヤフオク最安値取得）", type="primary", width="stretch"):
with st.spinner("ヤフオクの新着データを自動チェック中..."):
updated_rows = []
for idx, row in st.session_state.w_df.iterrows():
kw = row["商品名"]
target = row["狙う仕入れ価格"]

current_lowest = check_yahoo_auctions_html(kw)

if current_lowest is not None and current_lowest >= 100:
row["前回最安値"] = int(current_lowest)
if target > 0 and current_lowest <= target:
row["状態"] = "🔥 買い時アリ！"
else:
row["状態"] = "👀 巡回済"
else:
row["前回最安値"] = 0
row["状態"] = "❌ 出品なし"

updated_rows.append(row)
time.sleep(1.2)

new_df = pd.DataFrame(updated_rows)
new_df.to_csv(WATCH_FILE, index=False)
st.session_state.w_df = new_df
st.toast("ヤフオクの自動巡回が完了しました！", icon="🚀")
st.rerun()

st.markdown("### 📋 登録中の一覧（ヤフオク巡回に加え、eBayドル相場を手動入力できます）")
w_df_show = st.session_state.w_df.copy()
w_df_show.insert(0, "削除", False)
state_options = ["🆕 未チェック", "👀 巡回済", "🔥 買い時アリ！", "❌ 出品なし", "📦 仕入れ完了"]
edited_w_df = st.data_editor(
w_df_show,
column_config={
"削除": st.column_config.CheckboxColumn("削除", width="small"),
"商品名": st.column_config.TextColumn("商品名", required=True),
"狙う仕入れ価格": st.column_config.NumberColumn("狙う価格(円)", format="¥%d"),
"前回最安値": st.column_config.NumberColumn("ヤフオク最安(円)", format="¥%d", disabled=True),
"eBay相場(ドル)": st.column_config.NumberColumn("eBay相場(ドル入力)", format="$%.2f", min_value=0.0, step=10.0),
"状態": st.column_config.SelectboxColumn("ステータス", options=state_options),
},
width="stretch", hide_index=True, key="watch_editor"
)

saved_w = edited_w_df[edited_w_df["削除"] == False].copy()
saved_w = saved_w[["商品名", "狙う仕入れ価格", "前回最安値", "eBay相場(ドル)", "状態"]].reset_index(drop=True)
if not st.session_state.w_df.reset_index(drop=True).equals(saved_w):
saved_w.to_csv(WATCH_FILE, index=False)
st.session_state.w_df = saved_w
st.toast("💾 変更を自動保存しました！", icon="✅")
st.rerun()

st.divider()
st.markdown("### 🚀 詳細データ ＆ 手動リンク")
for idx, row in st.session_state.w_df.iterrows():
kw = row["商品名"]
target = row["狙う仕入れ価格"]
status = row["状態"]
prev_min = row["前回最安値"]
ebay_usd = row.get("eBay相場(ドル)", 0.0)

ebay_jpy = int(ebay_usd * current_rate)

# ① ヤフオクで拾った「実際の最安値」ベースの見込利益
if ebay_jpy > 0 and prev_min > 0:
est_profit_min = int((ebay_jpy * 0.85) - prev_min - 2000)
est_rate_min = (est_profit_min / ebay_jpy * 100) if ebay_jpy > 0 else 0
profit_text_min = f"¥{est_profit_min:,.0f} ({est_rate_min:.1f}%)"
color_min = "#1A7A42" if est_profit_min > 0 else "#C62828"
else:
profit_text_min = "巡回未実施" if ebay_jpy > 0 else "eBay相場未入力"
color_min = "#777777"

# ② 自分がエディタに入力した「狙う仕入れ価格（上限）」ベースの見込利益
if ebay_jpy > 0 and target > 0:
est_profit_tgt = int((ebay_jpy * 0.85) - target - 2000)
est_rate_tgt = (est_profit_tgt / ebay_jpy * 100) if ebay_jpy > 0 else 0
profit_text_tgt = f"¥{est_profit_tgt:,.0f} ({est_rate_tgt:.1f}%)"
color_tgt = "#1A7A42" if est_profit_tgt > 0 else "#C62828"
else:
profit_text_tgt = "狙い価格未入力" if ebay_jpy > 0 else "eBay相場未入力"
color_tgt = "#777777"

encoded_kw = urllib.parse.quote(kw)
price_param = f"&price_max={target}" if target > 0 else ""

mercari_url = f"https://jp.mercari.com/search?keyword={encoded_kw}&status=on_sale&sort=created_time{price_param}"
yahoo_url = f"https://auctions.yahoo.co.jp/search/search?p={encoded_kw}&va={encoded_kw}&exflg=1&b=1&n=50&s1=cbids&o1=a&wrmode=2"
ebay_live_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_kw}&LH_BIN=1&_sop=15"
ebay_sold_url = f"https://www.ebay.com/sch/i.html?_nkw={encoded_kw}&LH_Sold=1&LH_Complete=1"

col_name, col_prices, col_m, col_y, col_el, col_es = st.columns([2.5, 3.5, 1.5, 1.5, 1.5, 1.5])
with col_name:
st.markdown(f"**{kw}**")
if status == "🔥 買い時アリ！":
st.markdown(f"<span style='color:#e32b2b; font-weight:bold; font-size:0.85rem;'>{status}</span>", unsafe_allow_html=True)
else:
st.markdown(f"`{status}`")

with col_prices:
st.markdown(f"""
<span style='font-size:0.82rem; color:#444;'>
🇯🇵 ヤフオク最安: <strong>¥{prev_min:,.0f}</strong> (狙い: ¥{target:,.0f})<br>
🇺🇸 eBay最安換算: <strong>¥{ebay_jpy:,.0f}</strong> (${ebay_usd:.2f})<br>
💰 現最安値での利益: <strong style='color:{color_min};'>{profit_text_min}</strong><br>
🎯 狙い価格での利益: <strong style='color:{color_tgt};'>{profit_text_tgt}</strong>
</span>
""", unsafe_allow_html=True)

with col_m:
st.markdown(f'<a href="{mercari_url}" target="_blank" style="display:block; text-align:center; background:#e32b2b; color:white; padding:6px 2px; border-radius:4px; text-decoration:none; font-size:0.78rem; font-weight:bold;">🔴 メルカリ ↗</a>', unsafe_allow_html=True)
with col_y:
st.markdown(f'<a href="{yahoo_url}" target="_blank" style="display:block; text-align:center; background:#ffaa00; color:#1a1a1a; padding:6px 2px; border-radius:4px; text-decoration:none; font-size:0.78rem; font-weight:bold;">🟡 ヤフオク ↗</a>', unsafe_allow_html=True)
with col_el:
st.markdown(f'<a href="{ebay_live_url}" target="_blank" style="display:block; text-align:center; background:#0064d2; color:white; padding:6px 2px; border-radius:4px; text-decoration:none; font-size:0.78rem; font-weight:bold;">🔵 eBay最安 ↗</a>', unsafe_allow_html=True)
with col_es:
st.markdown(f'<a href="{ebay_sold_url}" target="_blank" style="display:block; text-align:center; background:#2d7a4f; color:white; padding:6px 2px; border-radius:4px; text-decoration:none; font-size:0.78rem; font-weight:bold;">🟢 eBay売切 ↗</a>', unsafe_allow_html=True)
st.write("")
else:
st.warning("現在、監視リストに登録されているキーワードはありません。")
st.write("システム稼働中")
