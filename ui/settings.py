import streamlit as st
import json
from utils.storage import stop_with_save
from logic.sync import (
    on_home_target_slider_change,
    on_target_distance_change,
    on_home_motor_slider_change,
    on_motor_input_change,
    on_home_run_slider_change,
    sync_run_time_from_display,
)
from logic.schedule import save_ab_profile


def render_settings_page():

    st.title("設定画面")

    # ==========================================
    # 初期値同期
    # ==========================================
    st.session_state.home_target_slider = float(st.session_state.target_distance_m)
    st.session_state.home_motor_slider = float(st.session_state.motor_speed_value)
    st.session_state.home_run_slider = float(st.session_state.run_time_display_value)

    # ==========================================
    # 目標距離
    # ==========================================
    distance_heading_color = "#66ccff" if st.session_state.sync_priority_mode == "distance" else "#d0d0d0"
    st.markdown(f"<h4 style='color:{distance_heading_color}'>目標距離 (m)</h4>", unsafe_allow_html=True)

    st.slider(
        "目標距離 (m)",
        0.0,
        100000.0,
        step=1.0,
        key="home_target_slider",
        on_change=on_home_target_slider_change,
    )

    st.number_input(
        "目標距離 (m)",
        min_value=0.0,
        max_value=100000.0,
        step=1.0,
        key="target_distance_m",
        on_change=on_target_distance_change,
    )

    # ==========================================
    # モーター速度
    # ==========================================
    speed_heading_color = "#66ccff" if st.session_state.sync_priority_mode == "speed" else "#d0d0d0"
    st.markdown(f"<h4 style='color:{speed_heading_color}'>モーター速度 (m/min)</h4>", unsafe_allow_html=True)

    st.slider(
        "モーター速度 (m/min)",
        0.0,
        10000.0,
        step=0.1,
        key="home_motor_slider",
        on_change=on_home_motor_slider_change,
    )

    st.number_input(
        "モーター速度 (m/min)",
        min_value=0.0,
        max_value=10000.0,
        step=0.1,
        key="motor_speed_value",
        on_change=on_motor_input_change,
    )

    # ==========================================
    # 運転時間
    # ==========================================
    time_heading_color = "#66ccff" if st.session_state.sync_priority_mode == "time" else "#d0d0d0"
    st.markdown(f"<h4 style='color:{time_heading_color}'>運転時間 (min)</h4>", unsafe_allow_html=True)

    st.slider(
        "運転時間 (min)",
        0.0,
        600.0,
        step=1.0,
        key="home_run_slider",
        on_change=on_home_run_slider_change,
    )

    st.number_input(
        "運転時間 (min)",
        min_value=0.0,
        max_value=600.0,
        step=1.0,
        key="run_time_display_value",
        on_change=sync_run_time_from_display,
    )

    # ==========================================
    # プロファイル保存
    # ==========================================
    st.markdown("### 条件セット")

    profile_options = ["A", "B"]
    selected_profile = st.selectbox("保存先プロファイル", profile_options, key="profile_select")

    if st.button("プロファイル保存"):
        save_ab_profile(selected_profile)
        st.success(f"プロファイル {selected_profile} を保存しました")

    # ==========================================
    # JSON エクスポート
    # ==========================================
    st.markdown("### 設定のエクスポート / インポート")

    export_data = {
        "target_distance_m": st.session_state.target_distance_m,
        "motor_speed_value": st.session_state.motor_speed_value,
        "run_time_display_value": st.session_state.run_time_display_value,
        "accel_distance_m": st.session_state.accel_distance_m,
        "decel_distance_m": st.session_state.decel_distance_m,
    }

    st.download_button(
        "設定を JSON で保存",
        data=json.dumps(export_data, ensure_ascii=False, indent=2),
        file_name="settings.json",
        mime="application/json",
    )

    # ==========================================
    # JSON インポート
    # ==========================================
    uploaded = st.file_uploader("設定ファイルを読み込む (JSON)", type=["json"])

    if uploaded is not None:
        try:
            data = json.load(uploaded)

            st.session_state.target_distance_m = float(data.get("target_distance_m", 0))
            st.session_state.motor_speed_value = float(data.get("motor_speed_value", 0))
            st.session_state.run_time_display_value = float(data.get("run_time_display_value", 0))
            st.session_state.accel_distance_m = float(data.get("accel_distance_m", 0))
            st.session_state.decel_distance_m = float(data.get("decel_distance_m", 0))

            st.success("設定を読み込みました")
            st.rerun()

        except Exception as e:
            st.error(f"読み込みエラー: {e}")

    # ==========================================
    # スマホ UI モード
    # ==========================================
    st.markdown("### スマホ UI モード")

    st.checkbox(
        "スマホ UI を有効にする",
        key="mobile_ui",
    )

    st.caption("入力変更で自動計算されます。")

    # ==========================================
    # 最後に stop_with_save()
    # ==========================================
    stop_with_save()
