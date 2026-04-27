import streamlit as st
import math


def render_winding_page():

    st.title("巻取り計算")

    st.subheader("巻取り計算")

    # ==============================
    # 運転時間
    # ==============================
    runtime = st.number_input(
        "運転時間 (min)",
        min_value=0.0,
        max_value=10000.0,
        value=60.0,
        step=1.0
    )

    # ==============================
    # 最終速度（surface_speeds の最後を使用）
    # ==============================
    if "surface_speeds" in st.session_state and st.session_state.surface_speeds:
        final_speed = st.session_state.surface_speeds[-1]
    else:
        final_speed = 0.0

    # 巻取り長さ
    length = final_speed * runtime
    st.write(f"巻取り長さ : {length:.1f} m")

    st.divider()

    # ==============================
    # ロール重量
    # ==============================
    basis = st.number_input("坪量 g/m²", 0.0, 500.0, 120.0)
    width = st.number_input("紙幅 m", 0.0, 10.0, 1.0)

    weight = length * width * basis / 1000
    st.write(f"ロール重量 : {weight:.1f} kg")

    st.divider()

    # ==============================
    # ロール径
    # ==============================
    core_d = st.number_input("コア径 m", 0.01, 1.0, 0.076)
    thickness = st.number_input("紙厚 mm", 0.01, 1.0, 0.10)

    thickness_m = thickness / 1000

    radius = math.sqrt((length * thickness_m / math.pi) + (core_d / 2) ** 2)
    diameter = radius * 2

    st.write(f"ロール径 : {diameter:.3f} m")

    st.divider()

    # ==============================
    # 残り運転時間・残量
    # ==============================
    target_length = st.number_input("目標巻取り長さ m", 0.0, 10000000.0, 5000.0)

    remaining = target_length - length

    if final_speed > 0:
        remaining_time = remaining / final_speed
    else:
        remaining_time = 0.0

    st.write(f"残り運転時間 : {remaining_time:.1f} min")

    if target_length > 0:
        remain_pct = remaining / target_length * 100
    else:
        remain_pct = 0.0

    st.write(f"残量 : {remain_pct:.1f} %")
