import streamlit as st
from datetime import datetime


def add_audit(item, before, after):
    """操作ログを追加"""
    st.session_state.audit_log.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "item": item,
        "before": before,
        "after": after
    })
