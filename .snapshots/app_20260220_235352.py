import streamlit as st

PASSWORD = "rollsync2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    pw = st.text_input("パスワードを入力してください", type="password")
    if pw == PASSWORD:
        st.session_state.authenticated = True
        st.rerun()
    else:
        st.stop()
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

# ==============================
# CSS・表示
# ==============================
st.markdown("""
<style>
body {background-color:#111;}
h2 {color:#00ffff;}
.diff-ok {color:#00ff88;}
.diff-ng {color:#ff4444;}
.big-speed {font-size:22px; font-weight:bold;}
.big-diff {font-size:22px; font-weight:bold;}
.roll-title {font-size:22px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

# ==============================
# グループカラー
# ==============================
GROUP_COLORS = [
    "#00FFFF", "#FF8800", "#00FF88", "#FF44AA",
    "#FFD700", "#8888FF", "#FF4444", "#44FFDD",
    "#CCCC00", "#AA66FF", "#00CCFF", "#FF6666"
]

# ==============================
# 初期値
# ==============================
if "motor_speed" not in st.session_state:
    st.session_state.motor_speed = 750.0
if "roll_count" not in st.session_state:
    st.session_state.roll_count = 6
if "run_time_min" not in st.session_state:
    st.session_state.run_time_min = 0.0

roll_radius = 0.30

# ==============================
# ⚙ モーター速度制御
# ==============================
st.markdown("<div class='roll-title'>SyncRoll Pro</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([3,0.6,0.9])
with col1:
    motor_label_col, motor_slider_col = st.columns([1.5,5.5])
    with motor_label_col:
        st.markdown("<div style='margin-top:6px'>モーター速度 (m/min)</div>", unsafe_allow_html=True)
    with motor_slider_col:
        st.slider(
            "モーター速度 (m/min)",
            0.0,1300.0,
            step=0.1,
            key="motor_slider",
            value=st.session_state.motor_speed,
            label_visibility="collapsed",
            on_change=lambda: st.session_state.update({
                "motor_speed":st.session_state.motor_slider,
                "motor_input":st.session_state.motor_slider
            })
        )
with col2:
    st.number_input(
        "数値入力",
        min_value=0.0,
        max_value=1300.0,
        step=0.1,
        key="motor_input",
        value=st.session_state.motor_speed,
        label_visibility="collapsed",
        on_change=lambda: st.session_state.update({
            "motor_speed":st.session_state.motor_input,
            "motor_slider":st.session_state.motor_input
        })
    )
with col3:
    run_label_col, run_input_col = st.columns([1.3,1.2])
    with run_label_col:
        st.markdown("<div style='margin-top:6px'>運転時間 (min)</div>", unsafe_allow_html=True)
    with run_input_col:
        st.number_input(
            "運転時間 (min)",
            min_value=0.0,
            step=1.0,
            key="run_time_min",
            value=st.session_state.run_time_min,
            label_visibility="collapsed"
        )
belt_speed = st.session_state.motor_speed
run_time_min = st.session_state.run_time_min

# ==============================
# 🏭 ロール制御
# ==============================
title_col, r_col = st.columns([7,2])
with title_col:
    st.markdown("<div class='roll-title'>ロール速度</div>", unsafe_allow_html=True)
with r_col:
    r_label_col, r_input_col = st.columns([1,1.2])
    with r_label_col:
        st.markdown("<div style='margin-top:6px'>R数</div>", unsafe_allow_html=True)
    with r_input_col:
        st.session_state.roll_count = st.number_input(
            "R数",
            min_value=1,
            max_value=12,
            step=1,
            value=st.session_state.roll_count,
            label_visibility="collapsed"
        )
R = st.session_state.roll_count

# ==============================
# 各ロール初期化（初回起動時すべてMaster ON）
# ==============================
for i in range(R):
    st.session_state.setdefault(f"pulley_{i}", 0.30)
    st.session_state.setdefault(f"diff_pct_{i}", 0.00)
    st.session_state.setdefault(f"group_{i}", i + 1)
    st.session_state.setdefault(f"master_{i}", True)  # 初回起動時で全MasterON
    st.session_state.setdefault(f"prev_master_{i}", st.session_state[f"pulley_{i}"])
    st.session_state.setdefault(f"prev_master_diff_{i}", st.session_state[f"diff_pct_{i}"])

# ==============================
# マスター整合性維持
# ==============================
def enforce_master_rules(changed_i=None):
    groups = {}
    for i in range(R):
        g = st.session_state[f"group_{i}"]
        groups.setdefault(g, []).append(i)

    for g, members in groups.items():
        masters = [i for i in members if st.session_state[f"master_{i}"]]

        if changed_i is not None and changed_i in members:
            if st.session_state[f"master_{changed_i}"]:
                for i in members:
                    if i != changed_i:
                        st.session_state[f"master_{i}"] = False
                st.session_state[f"prev_master_{changed_i}"] = st.session_state[f"pulley_{changed_i}"]
                st.session_state[f"prev_master_diff_{changed_i}"] = st.session_state[f"diff_pct_{changed_i}"]
            continue

        if len(masters) == 0:
            st.session_state[f"master_{members[0]}"] = True
        elif len(masters) > 1:
            for i in masters[1:]:
                st.session_state[f"master_{i}"] = False

# ==============================
# 同期反映
# ==============================
def sync_from_master(source_i):
    if not st.session_state[f"master_{source_i}"]:
        return

    group_id = st.session_state[f"group_{source_i}"]
    current_pulley = st.session_state[f"pulley_{source_i}"]
    prev_pulley = st.session_state[f"prev_master_{source_i}"]
    delta_pulley = current_pulley - prev_pulley
    st.session_state[f"prev_master_{source_i}"] = current_pulley

    current_diff = st.session_state[f"diff_pct_{source_i}"]
    prev_diff = st.session_state[f"prev_master_diff_{source_i}"]
    delta_diff = current_diff - prev_diff
    st.session_state[f"prev_master_diff_{source_i}"] = current_diff

    for j in range(R):
        if j != source_i and st.session_state[f"group_{j}"] == group_id:
            if abs(delta_pulley) > 1e-9:
                new_val = st.session_state[f"pulley_{j}"] + delta_pulley
                new_val = max(0.10, min(0.50,new_val))
                st.session_state[f"pulley_{j}"] = round(new_val,3)

                r = st.session_state[f"pulley_{j}"]
                if belt_speed == 0:
                    st.session_state[f"diff_pct_{j}"] = 0.00
                else:
                    surface = belt_speed*(roll_radius/r)
                    diff = (surface-belt_speed)/belt_speed*100
                    st.session_state[f"diff_pct_{j}"] = round(diff,2)
            elif abs(delta_diff) > 1e-9:
                new_diff = st.session_state[f"diff_pct_{j}"] + delta_diff
                st.session_state[f"diff_pct_{j}"] = round(new_diff,2)
                if belt_speed != 0:
                    new_r = roll_radius/(1+new_diff/100)
                    new_r = max(0.10, min(0.50,new_r))
                    st.session_state[f"pulley_{j}"] = round(new_r,3)

# ==============================
# 計算
# ==============================
def update_from_speed(i):
    r = st.session_state[f"pulley_{i}"]
    if belt_speed == 0:
        st.session_state[f"diff_pct_{i}"] = 0.00
    else:
        surface = belt_speed*(roll_radius/r)
        diff = (surface-belt_speed)/belt_speed*100
        st.session_state[f"diff_pct_{i}"] = round(diff,2)
    sync_from_master(i)

def update_from_diff(i):
    pct = st.session_state[f"diff_pct_{i}"]
    if belt_speed != 0:
        new_r = roll_radius/(1+pct/100)
        new_r = max(0.10, min(0.50,new_r))
        st.session_state[f"pulley_{i}"] = round(new_r,3)
    sync_from_master(i)

def adjust_pulley(i,delta):
    val = st.session_state[f"pulley_{i}"] + delta
    val = max(0.10, min(0.50,val))
    st.session_state[f"pulley_{i}"] = round(val,3)
    update_from_speed(i)

def reset_roll_values(i):
    st.session_state[f"pulley_{i}"] = 0.30
    update_from_speed(i)

# ==============================
# UI
# ==============================
cols = st.columns(R)
surface_speeds = []

for i in range(R):
    with cols[i]:
        st.markdown(f"<div class='roll-title'>R{i+1}</div>", unsafe_allow_html=True)

        st.selectbox("Group", list(range(1,R+1)),
                     key=f"group_{i}",
                     on_change=enforce_master_rules,
                     args=(i,))

        master_col, reset_col = st.columns(2)
        with master_col:
            st.checkbox("Master",
                        key=f"master_{i}",
                        on_change=enforce_master_rules,
                        args=(i,))
        with reset_col:
            st.button("リセット", key=f"reset_{i}", on_click=reset_roll_values, args=(i,))

        st.slider("Pulley (m)",0.10,0.50,
                  step=0.01,
                  key=f"pulley_{i}",
                  on_change=update_from_speed,
                  args=(i,))

        col_m, col_space, col_p = st.columns([1,2,1])
        with col_m:
            st.button("➖", key=f"m_{i}", on_click=adjust_pulley, args=(i,-0.01))
        with col_p:
            st.button("➕", key=f"p_{i}", on_click=adjust_pulley, args=(i,0.01))

        st.number_input("速度差 (%)",
                        step=0.01,
                        format="%.2f",
                        key=f"diff_pct_{i}",
                        on_change=update_from_diff,
                        args=(i,))

        if belt_speed == 0:
            surface = 0
        else:
            surface = belt_speed*(roll_radius/st.session_state[f"pulley_{i}"])
        surface = round(surface,1)
        surface_speeds.append(surface)

        diff = st.session_state[f"diff_pct_{i}"]
        color_class = "diff-ok" if abs(diff)<=1 else "diff-ng"
        distance_m = round(surface * run_time_min, 1)

        st.markdown(f"<div class='big-speed'>速度: {surface:.1f} m/min</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-diff {color_class}'>速度差: {diff:.2f}%</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='big-speed'>移動距離: {distance_m:.1f} m</div>", unsafe_allow_html=True)

enforce_master_rules()

# ==============================
# 図表示
# ==============================
fig,ax = plt.subplots(figsize=(12,4))
spacing = 1.2
min_radius = 0.12
max_radius = spacing * 0.45  # 隣接円と重ならない上限
speed_max = 10000.0
for i in range(R):
    color = GROUP_COLORS[(st.session_state[f"group_{i}"]-1)%len(GROUP_COLORS)]
    speed_ratio = min(1.0, surface_speeds[i] / speed_max) if belt_speed != 0 else 0.0
    radius = min_radius + (max_radius - min_radius) * speed_ratio
    circle = plt.Circle((i*spacing,0), radius, fill=False, linewidth=3, color=color)
    ax.add_patch(circle)
ax.set_xlim(-max_radius, max(0.1, (R-1)*spacing + max_radius))
ax.set_ylim(-(max_radius + 0.1), max_radius + 0.1)
ax.set_aspect("equal")
ax.axis("off")
st.pyplot(fig)
plt.close(fig)
