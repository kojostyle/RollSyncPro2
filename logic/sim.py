import streamlit as st
import time


# ==========================================
# 現在の運転速度を計算（加速・減速・遷移を含む）
# ==========================================
def calc_running_speed_mpm(elapsed_sec):
    """
    現在の運転速度を返す（m/min）
    加速 → 定速 → 減速 のプロファイルを反映
    """

    accel = st.session_state.accel_distance_m
    decel = st.session_state.decel_distance_m
    target_speed = st.session_state.motor_speed_value

    # 加速時間（秒）
    accel_time = accel / target_speed * 60 if target_speed > 0 else 0
    # 減速時間（秒）
    decel_time = decel / target_speed * 60 if target_speed > 0 else 0

    # 加速中
    if elapsed_sec < accel_time:
        return target_speed * (elapsed_sec / accel_time)

    # 減速開始前
    if elapsed_sec < st.session_state.run_time_minutes_value * 60 - decel_time:
        return target_speed

    # 減速中
    remain = st.session_state.run_time_minutes_value * 60 - elapsed_sec
    if remain > 0 and decel_time > 0:
        return target_speed * (remain / decel_time)

    return 0.0


# ==========================================
# プロファイル A 適用
# ==========================================
def apply_profile_A():
    st.session_state.accel_distance_m = 10.0
    st.session_state.decel_distance_m = 10.0
    st.session_state.motor_speed_value = 3000.0
    st.session_state.run_time_minutes_value = 30.0

    _record_speed_history(0, st.session_state.motor_speed_value)


# ==========================================
# プロファイル B 適用
# ==========================================
def apply_profile_B():
    st.session_state.accel_distance_m = 20.0
    st.session_state.decel_distance_m = 20.0
    st.session_state.motor_speed_value = 5000.0
    st.session_state.run_time_minutes_value = 60.0

    _record_speed_history(0, st.session_state.motor_speed_value)


# ==========================================
# 速度履歴を記録
# ==========================================
def _record_speed_history(t, v):
    st.session_state.speed_history_time.append(t)
    st.session_state.speed_history_value.append(v)


# ==========================================
# 停止処理（減速 → 保存）
# ==========================================
def stop_with_save():
    """
    減速停止中なら速度を 1 秒ごとに更新し、停止完了後に保存する。
    UI 側（ui/sim.py）の最後で呼ばれる。
    """

    if not st.session_state.operation_active:
        return

    # 減速中
    if st.session_state.stop_pending:
        elapsed = st.session_state.operation_elapsed_sec
        if st.session_state.operation_started_at:
            elapsed += max(0.0, time.time() - st.session_state.operation_started_at)

        # 減速速度
        if st.session_state.stop_decel_duration_sec > 0:
            p = min(
                1.0,
                max(0.0, time.time() - st.session_state.stop_requested_at)
                / st.session_state.stop_decel_duration_sec,
            )
            current_speed = st.session_state.stop_start_speed * (1.0 - p)
        else:
            current_speed = 0.0

        _record_speed_history(elapsed, current_speed)

        # 停止完了
        if current_speed <= 0.0:
            st.session_state.operation_active = False
            st.session_state.stop_pending = False
            st.session_state.speed_transition_label = ""
            return

        time.sleep(1)
        st.rerun()

    else:
        # 通常運転中 → 履歴記録
        elapsed = st.session_state.operation_elapsed_sec
        if st.session_state.operation_started_at:
            elapsed += max(0.0, time.time() - st.session_state.operation_started_at)

        current_speed = calc_running_speed_mpm(elapsed)
        _record_speed_history(elapsed, current_speed)

        time.sleep(1)
        st.rerun()
