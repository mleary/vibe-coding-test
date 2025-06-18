import streamlit as st

# Basic Hello World Streamlit app
st.title("Hello World!")
st.write("Welcome to your first Streamlit app!")

# Add some simple interactivity
name = st.text_input("Enter your name:")
if name:
    st.write(f"Hello, {name}!")

# Add a button for fun
if st.button("Say Hello"):
    st.balloons()
    st.success("Hello from Streamlit! 🎉")