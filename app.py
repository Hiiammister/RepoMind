import streamlit as st
import time
from core.github_client import parse_github_url, getReadme, get_repo_tree
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

with logs_container:
    st.subheader("Logs")
    log_box=st.empty()

if st.button("Analyze"):
    #log_box.text("Parsing URL...") debugging ...
    owner, repo_name=parse_github_url(Repo)
    files=get_repo_tree(owner, repo_name)
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
                    st.subheader("ReadMe Preview:") # Added ReadMe Preview section for better structure
                    st.subheader("Repo Info:") # Added Repo Info section for better structure
                    st.write(f"Total Files in Repo: {len(files)}")
                    with st.expander("Show All Files in Repo"): # Added expander to show all files in the repo on demand
                        st.text("\n".join(files))

                    with st.expander("Show README Content"): # Added expander to show README content on demand

                        st.text("\n".join(lines))
                        prompt=f"Summarize the following GitHub repository README content in a {Depth_Bar} manner:\n\n{readme_content}" # Updated prompt to include depth of explanation
                        tech_stack_prompt=f"Extract the tech stack used in the following README content:\n\n{readme_content}" # Added separate prompt to extract tech stack information from README

                        llm_summary=generate(prompt) 
                        llm_tech_stack=generate(tech_stack_prompt)

                        with results_container:
                            st.subheader("Repo Summary:")

                            if llm_summary: # Added check to ensure LLM summary is not None before displaying results
                                st.text(llm_summary)
                                st.text(llm_tech_stack)
                            else:
                                st.error("Failed to generate summary from LLM.Is it running?")
            else: 
                st.warning("No README found or failed to fetch README.")
            
    else:
        with st.spinner("Loading..."):
            time.sleep(2)
            st.error("Repo parsing failed!")
            
            log_box.text("Invalid GitHub URL")


    # st.write("You selected:", Depth_Bar) , debugging...



        
