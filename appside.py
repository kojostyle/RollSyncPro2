import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

if "status" not in st.session_state:
    st.session_state.status = "停止"
    st.session_state.distance = 0
    st.session_state.speed = 0

def show_home():
    st.title("Roll制御システム")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        st.metric("運転状態",st.session_state.status)
    with c2:
        st.metric("現在距離",f"{st.session_state.distance} m")
    with c3:
        st.metric("速度",f"{st.session_state.speed} rpm")
    with c4:
        st.metric("残距離","0 m")

    st.divider()

    st.markdown("""
    <style>
    div.stButton > button {
        height:80px;
        font-size:26px;
        font-weight:bold;
    }
    </style>
    """, unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        if st.button("▶ START",use_container_width=True):
            st.session_state.status="運転中"
    with c2:
        if st.button("■ STOP",use_container_width=True):
            st.session_state.status="停止"
    with c3:
        if st.button("⟳ RESET",use_container_width=True):
            st.session_state.distance=0

    st.divider()
    st.subheader("距離推移")

    chart_data = pd.DataFrame({"distance":[0,1,2,3,4]})
    st.line_chart(chart_data)


def show_run():
    st.title("運転設定")

    col1,col2 = st.columns(2)
    with col1:
        target = st.number_input("目標距離 (m)",value=10000)
        speed = st.number_input("速度 (rpm)",value=10000)
        acc = st.number_input("加速度",value=1000)
        dec = st.number_input("減速度",value=1000)

        if st.button("設定保存"):
            st.session_state.speed = speed

    with col2:
        st.subheader("状態")
        st.metric("現在状態",st.session_state.status)
        st.metric("設定速度",f"{st.session_state.speed} rpm")


def show_winding():
    st.title("巻取り計算")

    col1,col2 = st.columns(2)
    with col1:
        width = st.number_input("幅",value=500)
        thickness = st.number_input("厚み",value=0.05)
        core = st.number_input("内径",value=76)
        outer = st.number_input("外径",value=300)

    with col2:
        st.subheader("結果")
        st.metric("巻数","0")
        st.metric("距離","0 m")
        st.metric("重量","0 kg")


def show_roll():
    st.title("ロール管理")

    data = pd.DataFrame({
        "ID":[],
        "品種":[],
        "長さ":[],
        "状態":[]
    })

    st.dataframe(data,use_container_width=True)

    c1,c2,c3 = st.columns(3)
    with c1:
        st.button("追加",use_container_width=True)
    with c2:
        st.button("編集",use_container_width=True)
    with c3:
        st.button("削除",use_container_width=True)


def show_settings():
    st.title("設定")

    max_rpm = st.number_input("最大回転数",value=300000)
    max_dist = st.number_input("最大距離",value=100000)

    st.button("保存")


page = st.sidebar.radio(
    "メニュー",
    ["ホーム","運転","巻取り計算","ロール管理","設定"]
)

if page == "ホーム":
    show_home()
elif page == "運転":
    show_run()
elif page == "巻取り計算":
    show_winding()
elif page == "ロール管理":
    show_roll()
elif page == "設定":
    show_settings()
