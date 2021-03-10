"""
Pandas: 1.　データのインポート/前処理
        2.  基礎統計/代表値
        3.  データの可視化/傾向をつかむ

Streamlit:  4. インタラクティブダッシュボードの作成/データ分析しやすいようにボードを作成

-GitHub         5.　アプリをデプロイ 
-Sharing

Open data: RESAS: https://resas.go.jp/#1/01100
Data: 国民一人当たりの賃金
Graph library Plotly: https://plotly.com/python/
streamlit dashborad reference: https://share.streamlit.io/daniellewisdl/streamlit-cheat-sheet/app.py

チャートの種類:バブルチャート(三次元の情報を二次元で表せる)
        　　 :ラインチャート(pandasのデータからx軸をインデックスで固定し、y軸は列で指定表示)


"""

import pandas as pd 
import streamlit as st 
import pydeck as pdk
import plotly.express as px

st.write("日本の賃金データダッシュボード")

# load the data of csv file
df_jp_ind = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_全国_全産業.csv', encoding='shift_jis')
df_jp_category = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_全国_大分類.csv', encoding='shift_jis')
df_pref_ind = pd.read_csv('./code_file/csv_data/雇用_医療福祉_一人当たり賃金_都道府県_全産業.csv', encoding='shift_jis')

st.header("■2019年:一人あたり平均賃金のヒートマップ")

# loat the data of lat and lon for the Prefectures
jp_lat_lon = pd.read_csv("./code_file/pref_lat_lon.csv").rename(columns={"pref_name":"都道府県名"})

# Condition match
df_pref_map = df_pref_ind[(df_pref_ind["年齢"] == "年齢計") & (df_pref_ind["集計年"] == 2019)]
# concate df
df_pref_marge_map = pd.merge(df_pref_map, jp_lat_lon, on="都道府県名")
# normaization min_max 
df_pref_marge_map["一人当たりの賃金（相対値）"] = (df_pref_marge_map["一人当たり賃金（万円）"] - df_pref_marge_map["一人当たり賃金（万円）"].min()) / (df_pref_marge_map["一人当たり賃金（万円）"].max() - df_pref_marge_map["一人当たり賃金（万円）"].min())

## pydeck 
# setting params of view 
view = pdk.ViewState(
        longitude= 139.4130,
        latitude= 35.4122, 
        zoom=4,
        pich=40.5,
)
# setting layer
layer = pdk.Layer(
        "HeatmapLayer",
        data=df_pref_marge_map,
        opacity=0.4,  # 透明度
        get_position=["lon", "lat"], #  緯度軽度
        threshold=0.3,
        get_weight="一人当たりの賃金（相対値）" # 複数値があった場合どの列を可視化するかを指定
)
# rendering
layer_map = pdk.Deck(
        layers=layer,
        initial_view_state=view
)
st.pydeck_chart(layer_map)

show_df = st.checkbox("Show DataFrame")
if show_df == True:
        st.write(df_pref_marge_map)

st.header("■集計年別の一人あたり賃金 (万円)の推移")

df_ts_mean = df_jp_ind[(df_jp_ind["年齢"] == "年齢計")]
df_ts_mean = df_ts_mean.rename(columns={"一人当たり賃金（万円）":"全国_一人当たり賃金（万円）"})

df_pref_mean = df_pref_ind[(df_pref_ind["年齢"] == "年齢計")]
pref_list = df_pref_mean["都道府県名"].unique()

option_pref = st.selectbox(
        "都道府県",
        (pref_list))

df_pref_mean = df_pref_mean[df_pref_mean["都道府県名"] == option_pref]
df_pref_mean

# 結合
df_mean_line = pd.merge(df_ts_mean, df_pref_mean, on="集計年")
df_mean_line = df_mean_line[["集計年", "全国_一人当たり賃金（万円）", "一人当たり賃金（万円）"]]
df_mean_line = df_mean_line.set_index("集計年")
# plot line chart 
st.line_chart(df_mean_line)

##バブルチャート
#全国一人当たりの平均賃金のデータ（df_jp_ind）
st.header("■年齢階級別の全国一人当たり平均賃金（万円）")

df_mean_bubble = df_jp_ind[df_jp_ind["年齢"] != "年齢計"]

fig = px.scatter(df_mean_bubble,

        x="一人当たり賃金（万円）",
        y="年間賞与その他特別給与額（万円）",
        range_x=[150, 700],
        range_y=[0, 150],
        size="所定内給与額（万円）",

        size_max=38,
        color="年齢",
        animation_frame="集計年",
        animation_group="年齢"        
)

st.plotly_chart(fig)

# バーグラフ

st.header("■産業別の賃金推移/按产业列别的收入平均推移")
year_list = df_jp_category["集計年"].unique()

option_year = st.selectbox(
        "集計年",
        (year_list)

)

wage_list = ["一人当たり賃金（万円）", "所定内給与額（万円）", "年間賞与その他特別給与額（万円）"]
option_wage = st.selectbox(

        "賃金の種類",
        (wage_list)
)
df_mean_categ = df_jp_category[(df_jp_category["集計年"] == option_year)]
# scale
max_x = df_mean_categ[option_wage].max() + 50

fig = px.bar(df_mean_categ,
        x = option_wage,
        y = "産業大分類名",
        color="産業大分類名",
        animation_frame="年齢",
        range_x=[0,max_x],
        orientation="h",
        width=800,
        height=500
)

st.plotly_chart(fig)