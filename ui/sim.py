import streamlit as st
import time
import math
import matplotlib.pyplot as plt

from logic.sim import (
    calc_running_speed_mpm,
    apply_profile_A,
    apply_profile_B,
    stop_with_save,
)
from utils.audit import add_audit


def render_sim_page():

    # ==============================
    # シミュレーションパネル表示
    # ==============================
    if not st.session_state.show_sim_panel:
        return

    simulation_display_mode = (st.session_state.mobile_page == "sim")
    st.session_state.sim_profile_apply_to_current = simulation_display_mode

    disable_distance_input = (st.session_state.sync_priority_mode == "distance")
    disable_speed_input = (st.session_state.sync_priority_mode == "speed")
    disable_time_input = (st.session_state.sync_priority_mode == "time")

    # レイアウト
    if st.session_state.mobile_ui:
        col1 = st.container()
    else:
        col1, col2, col3 = st.columns([4.2, 0.2, 0.6])

    with col1:

        # ==============================
        # モーター速度表示
        # ==============================
        if not simulation_display_mode:
            motor_box = st.container(border=True)
            with motor_box:

                # 経過時間から現在速度を計算
                elapsed_for_speed = st.session_state.operation_elapsed_sec
                if st.session_state.operation_active and st.session_state.operation_started_at is not None:
                    elapsed_for_speed += max(0.0, time.time() - st.session_state.operation_started_at)

                running_motor_speed = (
                    calc_running_speed_mpm(elapsed_for_speed)
                    if st.session_state.operation_active else 0.0
                )

                # 速度遷移処理
                if st.session_state.speed_transition_active and st.session_state.speed_transition_started_at is not None:
                    dur = st.session_state.speed_transition_duration_sec
                    if dur > 0:
                        p = min(1.0, max(0.0, (time.time() - st.session_state.speed_transition_started_at) / dur))
                        v0 = st.session_state.speed_transition_from_speed
                        v1 = st.session_state.speed_transition_to_speed
                        running_motor_speed = v0 + (v1 - v0) * p

                        if p >= 1.0:
                            st.session_state.speed_transition_active = False
                            st.session_state.speed_transition_started_at = None
                            st.session_state.speed_transition_duration_sec = 0.0
                            st.session_state.speed_transition_from_speed = v1
                            st.session_state.speed_transition_to_speed = v1
                            st.session_state.speed_transition_label = ""
                    else:
                        st.session_state.speed_transition_active = False
                        st.session_state.speed_transition_started_at = None
                        st.session_state.speed_transition_duration_sec = 0.0
                        st.session_state.speed_transition_from_speed = st.session_state.motor_speed_value
                        st.session_state.speed_transition_to_speed = st.session_state.motor_speed_value
                        st.session_state.speed_transition_label = ""

                # 停止減速処理
                if st.session_state.stop_pending and st.session_state.stop_requested_at is not None:
                    if st.session_state.stop_decel_duration_sec > 0:
                        stop_progress = min(
                            1.0,
                            max(0.0, time.time() - st.session_state.stop_requested_at)
                            / st.session_state.stop_decel_duration_sec,
                        )
                        running_motor_speed = max(0.0, st.session_state.stop_start_speed * (1.0 - stop_progress))
                    else:
                        running_motor_speed = 0.0

                # UI 表示
                if st.session_state.mobile_ui:
                    st.markdown("<div class='big-speed'>モーター速度 (m/min)</div>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div class='roll-title' style='margin-top:2px'>運転中 {running_motor_speed:.1f}</div>",
                        unsafe_allow_html=True,
                    )
                    st.slider(
                        "モーター速度 (m/min)",
                        0.0,
                        10000.0,
                        step=0.1,
                        key="motor_speed_slider_value",
                        value=st.session_state.motor_speed_slider_value,
                        on_change=st.session_state.on_motor_slider_change,
                        disabled=disable_speed_input,
                    )
                else:
                    motor_label_col, motor_live_col, motor_slider_col = st.columns([1.6, 1.4, 4.8])
                    with motor_label_col:
                        st.markdown("<div class='big-speed'>モーター速度 (m/min)</div>", unsafe_allow_html=True)
                    with motor_live_col:
                        st.markdown(
                            f"<div class='roll-title' style='margin-top:2px'>運転中 {running_motor_speed:.1f}</div>",
                            unsafe_allow_html=True,
                        )
                    with motor_slider_col:
                        st.slider(
                            "モーター速度 (m/min)",
                            0.0,
                            10000.0,
                            step=0.1,
                            key="motor_speed_slider_value",
                            value=st.session_state.motor_speed_slider_value,
                            label_visibility="collapsed",
                            on_change=st.session_state.on_motor_slider_change,
                            disabled=disable_speed_input,
                        )

        # ==============================
        # 距離・時間計算
        # ==============================
        extra_distance_m = st.session_state.accel_distance_m + st.session_state.decel_distance_m

        actual_elapsed_seconds = st.session_state.operation_elapsed_sec
        if st.session_state.operation_active and st.session_state.operation_started_at is not None:
            actual_elapsed_seconds += max(0.0, time.time() - st.session_state.operation_started_at)

        actual_elapsed_seconds = max(0.0, actual_elapsed_seconds - st.session_state.time_display_offset_sec)
        actual_elapsed_min = actual_elapsed_seconds / 60.0

        # ==============================
        # プロファイル A / B
        # ==============================
        st.markdown("### プロファイル適用")

        colA, colB = st.columns(2)
        with colA:
            if st.button("プロファイル A 適用"):
                apply_profile_A()
                add_audit("プロファイル", "適用", "A")
                st.rerun()

        with colB:
            if st.button("プロファイル B 適用"):
                apply_profile_B()
                add_audit("プロファイル", "適用", "B")
                st.rerun()

        # ==============================
        # グラフ表示（速度推移）
        # ==============================
        st.markdown("### 速度推移グラフ")

        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(st.session_state.speed_history_time, st.session_state.speed_history_value, color="cyan")
        ax.set_xlabel("Time (sec)")
        ax.set_ylabel("Speed (m/min)")
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)

        # ==============================
        # 予定時刻
        # ==============================
        st.markdown("### 予定時刻")

        if st.session_state.target_distance_m > 0 and st.session_state.motor_speed_value > 0:
            remaining = st.session_state.target_distance_m - st.session_state.current_distance_m
            if remaining > 0:
                eta_min = remaining / st.session_state.motor_speed_value
                st.info(f"予定完了時刻: {eta_min:.1f} 分後")
            else:
                st.success("目標距離に到達しました")
        else:
            st.caption("目標距離が設定されていません")

        # ==============================
        # 低速 / 高速 / 停止ボタン
        # ==============================
        st.markdown("### 操作")

        btn1, btn2, btn3 = st.columns(3)

        with btn1:
            if st.button("低速運転"):
                st.session_state.speed_mode = "low"
                add_audit("運転", "低速", "")
                st.rerun()

        with btn2:
            if st.button("高速運転"):
                st.session_state.speed_mode = "normal"
                add_audit("運転", "高速", "")
                st.rerun()

        with btn3:
            if st.button("■ 停止"):
                st.session_state.stop_pending = True
                st.session_state.stop_requested_at = time.time()
                st.session_state.stop_start_speed = st.session_state.motor_speed_value
                add_audit("運転", "停止要求", "")
                st.rerun()

    # ==============================
    # 最後に stop_with_save()
    # ==============================
    if st.session_state.mobile_page == "sim":
        stop_with_save()
