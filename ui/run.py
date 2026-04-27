elif st.session_state.mobile_page == "run":
    st.write("運転画面")
if st.session_state.mobile_page == "run":
    render_mobile_run_page()
    stop_with_save()
