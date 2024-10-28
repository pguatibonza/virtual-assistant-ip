import streamlit as st

def login():
    st.title("Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "admin":
            st.success("Logged in successfully")
            return "token"
        else:
            st.error("Invalid username or password")
            
            
