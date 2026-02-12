import streamlit as st
import time
from core.github_client import parse_github_url
st.title("RepoMind")
st.subheader("A GitHub Repo Explainer")
Repo=st.text_input("Add the GitHub Repository you want me to explain","")


with st.sidebar:
    Depth_Bar=st.selectbox(
        "Depth of Explain:",
        ("Quick", "Standard", "Deep"),
    )
results_container=st.container()
logs_container=st.container()
with results_container:
    st.subheader("Main Results Area")

with logs_container:
    st.subheader("Logs")
    log_box=st.empty()

if st.button("Analyze"):
    #log_box.text("Parsing URL...") debugging ...
    owner, repo_name=parse_github_url(Repo)
    if owner and repo_name:
        log_box.text(f"Parsing URL...\nRepo detected:{owner}/{repo_name}")
    else:
        log_box.text("Invalid GitHub URL")


    # st.write("You selected:", Depth_Bar) , debugging...



        
