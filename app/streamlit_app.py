import streamlit as st

st.title("Talent Intelligence Platform")

st.write("Redrob AI Candidate Ranking Demo")

uploaded_file = st.file_uploader(
    "Upload Candidate File",
    type=["jsonl"]
)

if uploaded_file:
    st.success("File uploaded successfully")
    st.write("Ranking system ready.")