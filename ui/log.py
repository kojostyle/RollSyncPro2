import streamlit as st
import csv
import io
from datetime import datetime


def render_log_page():
    st.markdown("### 操作ログ")

    # ==============================
    # ボタン行（ログ消去 / CSV保存）
    # ==============================
    if st.session_state.mobile_ui:
        log_cols = st.columns([1, 1])
    else:
        log_cols = st.columns([1, 1, 3])

    # ログ消去
    with log_cols[0]:
        if st.button("ログ消去"):
            st.session_state.audit_log = []

    # CSV 保存
    with log_cols[1]:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["time", "item", "before", "after"])
        writer.writeheader()
        writer.writerows(st.session_state.audit_log)

        st.download_button(
            "CSV保存",
            data=output.getvalue().encode("utf-8-sig"),
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
        )

    # ==============================
    # ログ表示
    # ==============================
    if st.session_state.audit_log:
        st.dataframe(
            st.session_state.audit_log[-200:],  # 最新200件
            use_container_width=True
        )
    else:
        st.caption("ログはまだありません")
