import streamlit as st
import math


# ==========================================
# マスター整合性維持
# ==========================================
def enforce_master_rules(changed_i=None):
    R = st.session_state.roll_count

    groups = {}
    for i in range(R):
        g = st.session_state[f"group_{i}"]
        groups.setdefault(g, []).append(i)

    for g, members in groups.items():
        masters = [i for i in members if st.session_state[f"master_{i}"]]

        # 変更されたロールがある場合
        if changed_i is not None and changed_i in members:
            if st.session_state[f"master_{changed_i}"]:
                # 変更されたロールを唯一のマスターにする
                for i in members:
                    if i != changed_i:
                        st.session_state[f"master_{i}"] = False

                st.session_state[f"prev_master_{changed_i}"] = st.session_state[f"pulley_{changed_i}"]
                st.session_state[f"prev_master_diff_{changed_i}"] = st.session_state[f"diff_pct_{changed_i}"]
            continue

        # マスターがいない → 先頭をマスターに
        if len(masters) == 0:
            st.session_state[f"master_{members[0]}"] = True

        # マスターが複数 → 1つ以外 OFF
        elif len(masters) > 1:
            for i in masters[1:]:
                st.session_state[f"master_{i}"] = False


# ==========================================
# マスター同期反映
# ==========================================
def sync_from_master(source_i):
    R = st.session_state.roll_count
    belt_speed = st.session_state.motor_speed_value
    roll_radius = 0.30  # 固定値（あなたのアプリ仕様）

    if not st.session_state[f"master_{source_i}"]:
        return

    group_id = st.session_state[f"group_{source_i}"]

    # Pulley 差分
    current_pulley = st.session_state[f"pulley_{source_i}"]
    prev_pulley = st.session_state[f"prev_master_{source_i}"]
    delta_pulley = current_pulley - prev_pulley
    st.session_state[f"prev_master_{source_i}"] = current_pulley

    # Diff 差分
    current_diff = st.session_state[f"diff_pct_{source_i}"]
    prev_diff = st.session_state[f"prev_master_diff_{source_i}"]
    delta_diff = current_diff - prev_diff
    st.session_state[f"prev_master_diff_{source_i}"] = current_diff

    # 同じグループに反映
    for j in range(R):
        if j == source_i:
            continue
        if st.session_state[f"group_{j}"] != group_id:
            continue

        # Pulley の変化を反映
        if abs(delta_pulley) > 1e-9:
            new_val = st.session_state[f"pulley_{j}"] + delta_pulley
            new_val = max(0.10, min(0.50, new_val))
            st.session_state[f"pulley_{j}"] = round(new_val, 3)

            # Diff を再計算
            r = st.session_state[f"pulley_{j}"]
            if belt_speed == 0:
                st.session_state[f"diff_pct_{j}"] = 0.00
            else:
                surface = belt_speed * (roll_radius / r)
                diff = (surface - belt_speed) / belt_speed * 100
                st.session_state[f"diff_pct_{j}"] = round(diff, 2)

        # Diff の変化を反映
        elif abs(delta_diff) > 1e-9:
            new_diff = st.session_state[f"diff_pct_{j}"] + delta_diff
            st.session_state[f"diff_pct_{j}"] = round(new_diff, 2)

            # Pulley を再計算
            if belt_speed != 0:
                new_r = roll_radius / (1 + new_diff / 100)
                new_r = max(0.10, min(0.50, new_r))
                st.session_state[f"pulley_{j}"] = round(new_r, 3)


# ==========================================
# Pulley → Diff 計算
# ==========================================
def update_from_speed(i):
    belt_speed = st.session_state.motor_speed_value
    roll_radius = 0.30

    r = st.session_state[f"pulley_{i}"]

    if belt_speed == 0:
        st.session_state[f"diff_pct_{i}"] = 0.00
    else:
        surface = belt_speed * (roll_radius / r)
        diff = (surface - belt_speed) / belt_speed * 100
        st.session_state[f"diff_pct_{i}"] = round(diff, 2)

    sync_from_master(i)


# ==========================================
# Diff → Pulley 計算
# ==========================================
def update_from_diff(i):
    belt_speed = st.session_state.motor_speed_value
    roll_radius = 0.30

    pct = st.session_state[f"diff_pct_{i}"]

    if belt_speed != 0:
        new_r = roll_radius / (1 + pct / 100)
        new_r = max(0.10, min(0.50, new_r))
        st.session_state[f"pulley_{i}"] = round(new_r, 3)

    sync_from_master(i)


# ==========================================
# Pulley 微調整（＋／−）
# ==========================================
def adjust_pulley(i, delta):
    before = st.session_state[f"pulley_{i}"]

    val = st.session_state[f"pulley_{i}"] + delta
    val = max(0.10, min(0.50, val))
    st.session_state[f"pulley_{i}"] = round(val, 3)

    update_from_speed(i)

    from utils.audit import add_audit
    add_audit(f"R{i+1} Pulley(m)", before, st.session_state[f"pulley_{i}"])


# ==========================================
# ロール値リセット
# ==========================================
def reset_roll_values(i):
    before = st.session_state[f"pulley_{i}"]

    st.session_state[f"pulley_{i}"] = 0.30
    update_from_speed(i)

    from utils.audit import add_audit
    add_audit(f"R{i+1} リセット", before, st.session_state[f"pulley_{i}"])
