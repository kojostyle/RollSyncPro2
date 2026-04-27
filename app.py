import streamlit as st
from datetime import datetime

# ==============================
# UI モジュール
# ==============================
from ui.home import render_home_page
from ui.sim import render_sim_page
from ui.roll import render_roll_page
from ui.winding import render_winding_page
from ui.settings import render_settings_page
from ui.log import render_log_page

# ==============================
# 初期設定
# ==============================
st.set_page_config(
    page_title="RollSync Pro",
    layout="wide",
)

# ==============================
# CSS 読み込み
# ==============================
def load_css():
    with open("style.css", "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ==============================
# session_state 初期化
# ==============================
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

# ページ管理
init_state("mobile_page", "home")
init_state("mobile_ui", False)

# ロール関連
init_state("roll_count", 6)

# シミュレーション関連
init_state("operation_active", False)
init_state("operation_started_at", None)
init_state("operation_elapsed_sec", 0.0)
init_state("stop_pending", False)
init_state("stop_requested_at", None)
init_state("stop_start_speed", 0.0)
init_state("stop_decel_duration_sec", 3.0)

# モーター速度
init_state("motor_speed_value", 0.0)
init_state("motor_speed_slider_value", 0.0)

# 距離・時間
init_state("target_distance_m", 0.0)
init_state("run_time_display_value", 0.0)
init_state("run_time_minutes_value", 0.0)

# プロファイル
init_state("accel_distance_m", 10.0)
init_state("decel_distance_m", 10.0)

# 表示オフセット
init_state("time_display_offset_sec", 0.0)
init_state("distance_offset_sec", 0.0)

# ログ
init_state("audit_log", [])

# 速度履歴
init_state("speed_history_time", [])
init_state("speed_history_value", [])

# ==============================
# ページルーティング
# ==============================
page = st.session_state.mobile_page

if page == "home":
    render_home_page()

elif page == "sim":
    render_sim_page()

elif page == "roll":
    render_roll_page()

elif page == "winding":
    render_winding_page()

elif page == "settings":
    render_settings_page()

elif page == "log":
    render_log_page()
