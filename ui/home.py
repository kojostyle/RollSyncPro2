import streamlit as st
import time


def render_home_page():

    st.title("RollSync Pro ホーム")

    # ==============================
    # 運転状態
    # ==============================
    st.markdown("### 運転状態")

    if st.session_state.operation_active:
        if st.session_state.stop_pending:
            st.warning("減速停止中")
        else:
            st.success("運転中")
    else:
        st.info("停止中")

    # ==============================
    # 現在の速度・距離・時間
    # ==============================
    st.markdown("### 現在の状態")

    # 経過時間
    elapsed_seconds = st.session_state.operation_elapsed_sec
    if st.session_state.operation_active and st.session_state.operation_started_at:
        elapsed_seconds += max(0.0, time.time() - st.session_state.operation_started_at)

    elapsed_time_sec = max(0.0, elapsed_seconds - st.session_state.time_display_offset_sec)
    elapsed_min = elapsed_time_sec / 60.0

    # 距離
    elapsed_distance_sec = max(0.0, elapsed_seconds - st.session_state.distance_offset_sec)
    elapsed_distance_min = elapsed_distance_sec / 60.0

    # 速度
    motor_speed = st.session_state.motor_speed_value

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("速度 (m/min)", f"{motor_speed:.1f}")
    with col2:
        st.metric("経過時間 (min)", f"{elapsed_min:.2f}")
    with col3:
        st.metric("移動距離 (m)", f"{(motor_speed * elapsed_distance_min):.1f}")

    # ==============================
    # プロファイル情報
    # ==============================
    st.markdown("### プロファイル")

    profile_text = (
        f"加速距離: {st.session_state.accel_distance_m} m / "
        f"減速距離: {st.session_state.decel_distance_m} m / "
        f"目標距離: {st.session_state.target_distance_m} m"
    )
    st.caption(profile_text)

    # ==============================
    # 最近の操作ログ（最新5件）
    # ==============================
    st.markdown("### 最近の操作ログ")

    if st.session_state.audit_log:
        recent = st.session_state.audit_log[-5:]
        for row in recent:
            st.write(f"🕒 {row['time']} — {row['item']} : {row['before']} → {row['after']}")
    else:
        st.caption("ログはまだありません")

    # ==============================
    # ページナビゲーション
    # ==============================
    st.markdown("### メニュー")

    if st.session_state.mobile_ui:
        b1, b2 = st.columns(2)
        with b1:
            if st.button("シミュレーション"):
                st.session_state.mobile_page = "sim"
                st.rerun()
        with b2:
            if st.button("ロール制御"):
                st.session_state.mobile_page = "roll"
                st.rerun()

        b3, b4 = st.columns(2)
        with b3:
            if st.button("巻取り計算"):
                st.session_state.mobile_page = "winding"
                st.rerun()
        with b4:
            if st.button("設定"):
                st.session_state.mobile_page = "settings"
                st.rerun()

        if st.button("操作ログ"):
            st.session_state.mobile_page = "log"
            st.rerun()

    else:
        nav_cols = st.columns(6)
        labels = ["シミュレーション", "ロール制御", "巻取り計算", "設定", "操作ログ", "ホーム"]
        pages = ["sim", "roll", "winding", "settings", "log", "home"]

        for col, label, page in zip(nav_cols, labels, pages):
            with col:
                if st.button(label, use_container_width=True):
                    st.session_state.mobile_page = page
                    st.rerun()
