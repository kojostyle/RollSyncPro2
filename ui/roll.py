import streamlit as st
import time
import math
import matplotlib.pyplot as plt

from logic.roll import (
    enforce_master_rules,
    sync_from_master,
    update_from_speed,
    update_from_diff,
    adjust_pulley,
    reset_roll_values,
)
from utils.audit import add_audit
from utils.operation import (
    begin_operation,
    request_stop,
    finalize_stop,
    save_inputs_to_file,
)
from ui.log import render_log_page


GROUP_COLORS = [
    "#66ccff", "#ffcc66", "#99ff99", "#ff9999",
    "#cc99ff", "#ffccff", "#cccccc", "#99ccff",
]


def render_roll_page():

    # ==============================
    # 前処理（速度・時間・距離）
    # ==============================
    belt_speed = st.session_state.motor_speed_value
    run_time_min = st.session_state.run_time_minutes_value

    elapsed_seconds = st.session_state.operation_elapsed_sec
    if st.session_state.operation_active and st.session_state.operation_started_at is not None:
        elapsed_seconds += max(0.0, time.time() - st.session_state.operation_started_at)

    elapsed_time_sec = max(0.0, elapsed_seconds - st.session_state.time_display_offset_sec)
    elapsed_run_min = elapsed_time_sec / 60.0

    elapsed_distance_sec = max(0.0, elapsed_seconds - st.session_state.distance_offset_sec)
    elapsed_distance_min = elapsed_distance_sec / 60.0

    extra_distance_m = st.session_state.accel_distance_m + st.session_state.decel_distance_m

    # 減速停止完了処理
    if st.session_state.stop_pending and st.session_state.stop_requested_at is not None:
        if st.session_state.stop_decel_duration_sec > 0 and (
            time.time() - st.session_state.stop_requested_at
        ) >= st.session_state.stop_decel_duration_sec:
            finalize_stop()
            add_audit("運転状態", "減速停止中", "停止")
            st.rerun()

    # ==============================
    # R数入力
    # ==============================
    if st.session_state.mobile_ui:
        st.markdown("<div class='roll-title'>ロール速度</div>", unsafe_allow_html=True)
        prev_r = st.session_state.roll_count
        st.session_state.roll_count = st.number_input(
            "R数", min_value=1, max_value=12, step=1, value=st.session_state.roll_count
        )
        add_audit("R数", prev_r, st.session_state.roll_count)
    else:
        title_col, r_label_col, r_input_col, r_spacer_col = st.columns([2.0, 0.45, 0.75, 6.8])
        with title_col:
            st.markdown("<div class='roll-title'>ロール速度</div>", unsafe_allow_html=True)
        with r_label_col:
            st.markdown("<div class='field-label'>R数</div>", unsafe_allow_html=True)
        with r_input_col:
            prev_r = st.session_state.roll_count
            st.session_state.roll_count = st.number_input(
                "R数",
                min_value=1,
                max_value=12,
                step=1,
                value=st.session_state.roll_count,
                label_visibility="collapsed",
            )
            add_audit("R数", prev_r, st.session_state.roll_count)

    R = st.session_state.roll_count

    # ==============================
    # ロール初期化
    # ==============================
    for i in range(R):
        st.session_state.setdefault(f"pulley_{i}", 0.30)
        st.session_state.setdefault(f"diff_pct_{i}", 0.00)
        st.session_state.setdefault(f"group_{i}", i + 1)
        st.session_state.setdefault(f"master_{i}", True)
        st.session_state.setdefault(f"prev_master_{i}", st.session_state[f"pulley_{i}"])
        st.session_state.setdefault(f"prev_master_diff_{i}", st.session_state[f"diff_pct_{i}"])

    # ==============================
    # UI（pulley/diff/group/master）
    # ==============================
    if st.session_state.mobile_ui:
        cols = st.columns(2)
    else:
        cols = st.columns(R)

    surface_speeds = []

    roll_radius = 0.30  # 固定値（あなたのアプリ仕様）

    for i in range(R):
        with cols[i % len(cols)]:
            st.markdown(f"<div class='roll-title'>R{i+1}</div>", unsafe_allow_html=True)

            # Group
            before_group = st.session_state[f"group_{i}"]
            st.selectbox(
                "Group",
                list(range(1, R + 1)),
                key=f"group_{i}",
                on_change=enforce_master_rules,
                args=(i,),
            )
            add_audit(f"R{i+1} Group", before_group, st.session_state[f"group_{i}"])

            # Master / Reset
            master_col, reset_col = st.columns(2)
            with master_col:
                before_master = st.session_state[f"master_{i}"]
                st.checkbox(
                    "Master",
                    key=f"master_{i}",
                    on_change=enforce_master_rules,
                    args=(i,),
                )
                add_audit(f"R{i+1} Master", before_master, st.session_state[f"master_{i}"])
            with reset_col:
                st.button("リセット", key=f"reset_{i}", on_click=reset_roll_values, args=(i,))

            # Pulley
            before_pulley = st.session_state[f"pulley_{i}"]
            st.slider(
                "Pulley (m)",
                0.10,
                0.50,
                step=0.01,
                key=f"pulley_{i}",
                on_change=update_from_speed,
                args=(i,),
            )
            add_audit(f"R{i+1} Pulley(m)", before_pulley, st.session_state[f"pulley_{i}"])

            col_m, col_space, col_p = st.columns([1, 2, 1])
            with col_m:
                st.button("➖", key=f"m_{i}", on_click=adjust_pulley, args=(i, -0.01))
            with col_p:
                st.button("➕", key=f"p_{i}", on_click=adjust_pulley, args=(i, 0.01))

            # Diff
            before_diff = st.session_state[f"diff_pct_{i}"]
            st.number_input(
                "速度差 (%)",
                step=0.01,
                format="%.2f",
                key=f"diff_pct_{i}",
                on_change=update_from_diff,
                args=(i,),
            )
            add_audit(f"R{i+1} 速度差(%)", before_diff, st.session_state[f"diff_pct_{i}"])

            # 表示速度
            if belt_speed == 0:
                surface = 0
            else:
                surface = belt_speed * (roll_radius / st.session_state[f"pulley_{i}"])
            surface = round(surface, 1)
            surface_speeds.append(surface)

            diff = st.session_state[f"diff_pct_{i}"]
            color_class = "diff-ok" if abs(diff) <= 1 else "diff-ng"

            cruise_distance_m = surface * elapsed_distance_min
            accel_decel_distance_m = extra_distance_m if elapsed_distance_sec > 0 else 0.0
            distance_m = round(cruise_distance_m + accel_decel_distance_m, 1)

            st.markdown(f"<div class='big-speed'>速度: {surface:.1f} m/min</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='big-diff {color_class}'>速度差: {diff:.2f}%</div>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<div class='big-speed'>移動距離: {distance_m:.1f} m</div>", unsafe_allow_html=True)
            st.caption(
                f"内訳: 定速 {cruise_distance_m:.1f} m + 加減速 {accel_decel_distance_m:.1f} m"
            )

    # ==============================
    # リスク判定
    # ==============================
    max_abs_diff = max([abs(st.session_state[f"diff_pct_{i}"]) for i in range(R)] or [0.0])
    risk_score = 0
    if belt_speed > 3000:
        risk_score += 1
    if max_abs_diff > 1:
        risk_score += 1
    if max_abs_diff > 3:
        risk_score += 2
    if run_time_min > 60:
        risk_score += 1
    if R >= 10:
        risk_score += 1

    if risk_score >= 4:
        risk_label = "HIGH"
        risk_class = "risk-high"
    elif risk_score >= 2:
        risk_label = "MEDIUM"
        risk_class = "risk-mid"
    else:
        risk_label = "LOW"
        risk_class = "risk-low"

    st.markdown("### リスク判定")
    st.markdown(
        f"<div class='{risk_class}'>Risk: {risk_label} (score={risk_score}, max差分={max_abs_diff:.2f}%)</div>",
        unsafe_allow_html=True,
    )

    # ==============================
    # 運転前チェック
    # ==============================
    if st.session_state.show_precheck:
        st.markdown("### 運転前チェック")
        if st.session_state.mobile_ui:
            st.checkbox("機械点検済み", key="check_machine")
            st.checkbox("材料条件確認済み", key="check_material")
            st.checkbox("安全確認済み", key="check_safety")
        else:
            ck1, ck2, ck3 = st.columns(3)
            with ck1:
                st.checkbox("機械点検済み", key="check_machine")
            with ck2:
                st.checkbox("材料条件確認済み", key="check_material")
            with ck3:
                st.checkbox("安全確認済み", key="check_safety")

        checklist_ok = (
            st.session_state.check_machine
            and st.session_state.check_material
            and st.session_state.check_safety
        )
    else:
        checklist_ok = True

    start_blocked = (not checklist_ok) or (risk_label == "HIGH")

    # ==============================
    # 運転ボタン
    # ==============================
    is_low_active = st.session_state.operation_active and (st.session_state.speed_mode == "low") and (not st.session_state.stop_pending)
    is_high_active = st.session_state.operation_active and (st.session_state.speed_mode == "normal") and (not st.session_state.stop_pending)
    is_stop_active = st.session_state.stop_pending

    if st.session_state.mobile_ui:
        st.number_input(
            "低速 (m/min)",
            min_value=0.0,
            max_value=10000.0,
            step=0.1,
            key="low_speed_mpm_input",
            value=st.session_state.low_speed_mpm_cfg,
            on_change=on_low_speed_input_change,
        )

        btn_row1_col1, btn_row1_col2 = st.columns(2)
        with btn_row1_col1:
            if st.button(
                "低速運転",
                type="primary" if is_low_active else "secondary",
                use_container_width=True,
                disabled=(start_blocked and not st.session_state.operation_active),
            ):
                was_active = st.session_state.operation_active
                begin_operation(low_speed=True)
                add_audit("運転状態", "停止" if not was_active else "運転中", "運転開始")
                st.rerun()

        with btn_row1_col2:
            if st.button(
                "高速運転",
                type="primary" if is_high_active else "secondary",
                use_container_width=True,
                disabled=(start_blocked and not st.session_state.operation_active),
            ):
                was_active = st.session_state.operation_active
                begin_operation(low_speed=False)
                add_audit("運転状態", "停止" if not was_active else "運転中", "運転開始")
                st.rerun()

        btn_row2_col1, btn_row2_col2 = st.columns(2)
        with btn_row2_col1:
            if st.button(
                "■ 停止",
                type="primary" if is_stop_active else "secondary",
                use_container_width=True,
                disabled=(not st.session_state.operation_active),
            ):
                request_stop(elapsed_seconds)

        with btn_row2_col2:
            if st.button("距離リセット", use_container_width=True):
                before_elapsed = elapsed_distance_min
                st.session_state.distance_offset_sec = max(0.0, elapsed_seconds)
                add_audit("移動距離リセット(min)", round(before_elapsed, 4), 0.0)
                st.rerun()

        status_col = st.container()

    else:
        low_input_col, low_col, start_col, stop_col, reset_col, status_col = st.columns(
            [1.35, 1.05, 1.05, 1.05, 1.0, 3.0]
        )

        with low_input_col:
            st.number_input(
                "低速 (m/min)",
                min_value=0.0,
                max_value=10000.0,
                step=0.1,
                key="low_speed_mpm_input",
                value=st.session_state.low_speed_mpm_cfg,
                on_change=on_low_speed_input_change,
            )

        with low_col:
            if st.button(
                "低速運転",
                type="primary" if is_low_active else "secondary",
                use_container_width=True,
                disabled=(start_blocked and not st.session_state.operation_active),
            ):
                was_active = st.session_state.operation_active
                begin_operation(low_speed=True)
                add_audit("運転状態", "停止" if not was_active else "運転中", "運転開始")
                st.rerun()

        with start_col:
            if st.button(
                "高速運転",
                type="primary" if is_high_active else "secondary",
                use_container_width=True,
                disabled=(start_blocked and not st.session_state.operation_active),
            ):
                was_active = st.session_state.operation_active
                begin_operation(low_speed=False)
                add_audit("運転状態", "停止" if not was_active else "運転中", "運転開始")
                st.rerun()

        with stop_col:
            if st.button(
                "■ 停止",
                type="primary" if is_stop_active else "secondary",
                use_container_width=True,
                disabled=(not st.session_state.operation_active),
            ):
                request_stop(elapsed_seconds)

        with reset_col:
            if st.button("距離リセット", use_container_width=True):
                before_elapsed = elapsed_distance_min
                st.session_state.distance_offset_sec = max(0.0, elapsed_seconds)
                add_audit("移動距離リセット(min)", round(before_elapsed, 4), 0.0)
                st.rerun()

    # ==============================
    # ステータス表示
    # ==============================
    with status_col:
        if st.session_state.stop_pending:
            st.warning("減速停止中")
            st.caption(f"経過時間: {elapsed_run_min:.2f} min")
        elif st.session_state.operation_active and st.session_state.speed_transition_label:
            st.warning(st.session_state.speed_transition_label)
            st.caption(f"経過時間: {elapsed_run_min:.2f} min")
        elif st.session_state.operation_active:
            st.success("運転中")
            st.caption(f"経過時間: {elapsed_run_min:.2f} min")
        else:
            if not checklist_ok:
                st.warning("チェックリスト未完了のため開始不可")
            elif risk_label == "HIGH":
                st.error("Risk HIGHのため開始不可")
            else:
                st.info("待機中")

    # ==============================
    # ロール回転モニター
    # ==============================
    if st.session_state.show_roll_monitor:
        st.markdown("### ロール回転モニター")

        fig, ax = plt.subplots(figsize=(12, 4))
        fig.patch.set_facecolor("#111111")
        ax.set_facecolor("#111111")

        spacing = 1.2
        min_radius = 0.12
        max_radius = spacing * 0.45
        speed_max = 10000.0

        for i in range(R):
            color = GROUP_COLORS[(st.session_state[f"group_{i}"] - 1) % len(GROUP_COLORS)]
            speed_ratio = min(1.0, surface_speeds[i] / speed_max) if belt_speed != 0 else 0.0
            radius = min_radius + (max_radius - min_radius) * speed_ratio

            cx = i * spacing
            cy = 0.0

            circle = plt.Circle((cx, cy), radius, fill=False, linewidth=3, color=color)
            ax.add_patch(circle)

            if st.session_state.operation_active:
                visual_rpm = min(6.0, max(0.0, surface_speeds[i] / 500.0))
                angle = ((2.0 * math.pi) * visual_rpm * (elapsed_seconds / 60.0)) + (i * 0.35)
            else:
                angle = math.pi / 2.0

            hand_len = radius * 0.85
            hx = cx + hand_len * math.cos(angle)
            hy = cy + hand_len * math.sin(angle