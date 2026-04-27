import streamlit as st

def show_winding_calc():

    st.title("巻取り計算")

    runtime = st.number_input("運転時間 (min)",0.0,10000.0,60.0)

    speed = st.number_input("速度 (m/min)",0.0,2000.0,500.0)

    length = runtime * speed

    st.write(f"巻取り長さ : {length:.1f} m")
