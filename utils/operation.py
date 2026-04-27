import streamlit as st
import time


def begin_operation(low_speed=False):
    """運転開始"""
    st.session_state.operation_active = True
    st.session_state.stop_pending = False
    st.session_state.operation_started_at = time.time()
    st.session_state.speed_mode = "low" if low_speed else "normal"

    if low_speed:
        st.session_state.motor_speed_value = st.session_state.low_speed_mpm_cfg


def request_stop(elapsed_seconds):
    """停止要求"""
    st.session_state.stop_pending = True
    st.session_state.stop_requested_at = time.time()
    st.session_state.stop_start_speed = st.session_state.motor_speed_value


def finalize_stop():
    """停止完了"""
    st.session_state.operation_active = False
    st.session_state.stop_pending = False
    st.session_state.motor_speed_value = 0.0
    st.session_state.speed_transition_label = ""


def save_inputs_to_file():
    """入力値を保存（必要なら CSV や JSON に拡張可能）"""
    pass
