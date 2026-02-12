import streamlit as st
import time
from core.github_client import parse_github_url, getReadme
from core.ollama_client import generate
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
        readme_content=getReadme(owner, repo_name)
        with st.spinner("Loading..."):
            time.sleep(5)
            st.success("Repo Parsed Successfully!")
            log_box.text(f"Repo : {owner}/{repo_name}")
            log_box.text(f"Fetching README content...")
            if readme_content:
                lines=readme_content.splitlines()[:30]  # Show only first 30 lines for brevity

                with results_container:
                    st.subheader("ReadMe Preview:")
                    with st.expander("Show README Content"):
                        st.text("\n".join(lines))
                        prompt=f"Summarize the following GitHub repository README content in a {Depth_Bar} manner:\n\n{readme_content}"
                        llm_summary=generate(prompt)
                        with results_container:
                            st.subheader("LLM Generated Summary:")
                            if llm_summary:
                                st.text(llm_summary)
                            else:
                                st.error("Failed to generate summary from LLM.")
            else: 
                st.warning("No README found or failed to fetch README.")
            
    else:
        with st.spinner("Loading..."):
            time.sleep(2)
            st.error("Repo parsing failed!")
            
            log_box.text("Invalid GitHub URL")


    # st.write("You selected:", Depth_Bar) , debugging...



        
