import streamlit as st
import time

from core.github_client import parse_github_url, getReadme, get_repo_tree, get_file_content
from core.ollama_client import generate
from core.file_selector import select_files
from core.synthesizer import synthesize_report
from core.summarizer import summarize_file
from core.exporter import report_to_markdown

st.title("RepoMind")
st.subheader("A GitHub Repo Explainer")

Repo = st.text_input("Add the GitHub Repository you want me to explain", "")

with st.sidebar:
    Depth_Bar = st.selectbox("Depth of Explain:", ("Quick", "Standard", "Deep"))
    include_tests = st.checkbox("Include tests", value=False)
    include_docs = st.checkbox("Include docs", value=False)
    max_files = st.slider("Max files to select", 10, 100, 35)

results_container = st.container()
logs_container = st.container()

with logs_container:
    st.subheader("Logs")
    log_box = st.empty()

# -----------------------
# Session State Defaults
# -----------------------
if "analyzed" not in st.session_state:
    st.session_state.analyzed = False
if "owner" not in st.session_state:
    st.session_state.owner = None
if "repo_name" not in st.session_state:
    st.session_state.repo_name = None
if "final_report" not in st.session_state:
    st.session_state.final_report = None

# ✅ download state for README summary (always visible after parse)
if "summary_text" not in st.session_state:
    st.session_state.summary_text = None
if "summary_md" not in st.session_state:
    st.session_state.summary_md = None

# -----------------------
# Analyze Button
# -----------------------
if st.button("Analyze"):
    owner, repo_name = parse_github_url(Repo)
    if owner and repo_name:
        st.session_state.owner = owner
        st.session_state.repo_name = repo_name
        st.session_state.analyzed = True

        # Clear prior run caches
        st.session_state.pop("files", None)
        st.session_state.pop("auto_selected", None)
        st.session_state.pop("checked", None)
        st.session_state.pop("loaded_files", None)
        st.session_state.pop("fetch_stats", None)
        st.session_state.pop("final_report", None)
        st.session_state.pop("summary_text", None)
        st.session_state.pop("summary_md", None)

        log_box.text(f"Repo: {owner}/{repo_name}\nParsing URL...")
    else:
        st.session_state.analyzed = False
        log_box.text("Invalid GitHub URL")

# -----------------------
# Main App
# -----------------------
if st.session_state.analyzed:
    owner = st.session_state.owner
    repo_name = st.session_state.repo_name

    with results_container:
        st.success("URL Parsed Successfully!")

        # ✅ ALWAYS SHOW DOWNLOAD (disabled until summary generated)
        st.subheader("Download")
        download_slot= st.empty()
        download_slot.download_button(
            "Download README Summary",
            data=(st.session_state.get("summary_text") or ""),
            file_name="repo_summary.txt",
            mime="text/plain",
            disabled=(st.session_state.get("summary_text") is None),
            key="download_summary_btn"

        )
        

    with st.spinner("Loading..."):
        time.sleep(1)

    # Fetch repo tree once
    if "files" not in st.session_state:
        st.session_state.files = get_repo_tree(owner, repo_name)

    files = st.session_state.files

    with results_container:
        st.subheader("Repository Files:")
        st.write(f"Total Files in Repo: {len(files)}")
        st.write("First 100 files:")
        st.code("\n".join(files[:100]))

    # Smart selection
    if "auto_selected" not in st.session_state:
        st.session_state.auto_selected = select_files(
            files,
            max_files=max_files,
            include_tests=include_tests,
            include_docs=include_docs,
        )

    auto_selected = st.session_state.auto_selected

    # Selection form
    with results_container:
        st.subheader(f"Selected: {len(auto_selected)} files")

        with st.form("file_selection_form"):
            temp_checked = []
            for p in auto_selected:
                if st.checkbox(p, value=True, key=f"file_{p}"):
                    temp_checked.append(p)

            submitted = st.form_submit_button("Load Selected Files")

    if submitted:
        st.session_state.checked = temp_checked
        st.session_state.pop("loaded_files", None)
        st.session_state.pop("fetch_stats", None)
        st.session_state.pop("final_report", None)

    checked = st.session_state.get("checked", auto_selected)

    with results_container:
        st.write(f"Selected (after unchecking): {len(checked)}")

    # Fetch file contents
    loaded = {}
    if "checked" in st.session_state:
        if "loaded_files" not in st.session_state:
            skipped_large = 0
            skipped_binary = 0
            errors = 0

            for p in checked:
                content, status = get_file_content(owner, repo_name, p)

                if status == "ok":
                    loaded[p] = content
                elif status == "skip_large":
                    skipped_large += 1
                elif status == "skip_binary":
                    skipped_binary += 1
                else:
                    errors += 1

            st.session_state.loaded_files = loaded
            st.session_state.fetch_stats = (skipped_large, skipped_binary, errors)
        else:
            loaded = st.session_state.loaded_files

        skipped_large, skipped_binary, errors = st.session_state.fetch_stats

        with results_container:
            st.subheader("File Content Fetch Results")
            st.write(
                f"Loaded {len(loaded)} files, "
                f"skipped {skipped_large} large files, "
                f"skipped {skipped_binary} binary files, "
                f"errors {errors}"
            )

            if loaded:
                chosen_file = st.selectbox("Preview a file", list(loaded.keys()), key="preview_file")
                st.code(loaded[chosen_file][:4000])

    # -----------------------
    # Milestone C — Map → Reduce (optional)
    # -----------------------
    if "loaded_files" in st.session_state and st.session_state.loaded_files:
        with results_container:
            st.subheader("Milestone C — Full Repository Explanation")

            if st.button("Generate Full Explanation", key="gen_full_expl"):
                file_summaries = []
                items = list(st.session_state.loaded_files.items())
                total = len(items)

                progress = st.progress(0.0)

                for i, (path, content) in enumerate(items):
                    file_summaries.append(summarize_file(path, content))
                    progress.progress((i + 1) / total)

                repo_meta = {
                    "repo": f"{owner}/{repo_name}",
                    "total_files_in_repo": len(files),
                    "selected_files_count": len(st.session_state.loaded_files),
                }

                final_report = synthesize_report(repo_meta, file_summaries, depth=Depth_Bar)
                st.session_state.final_report = final_report

                st.success("Full explanation generated!")
                st.text(final_report)

    # -----------------------
    # README + Llama summary (this enables download button)
    # -----------------------
    readme_content = getReadme(owner, repo_name)

    with results_container:
        st.subheader("Repo Info:")
        st.write(f"Repo: {owner}/{repo_name}")

    if readme_content:
        lines = readme_content.splitlines()[:30]

        with results_container:
            st.subheader("README Preview:")
            with st.expander("Show README Content (first 30 lines)"):
                st.text("\n".join(lines))

            st.subheader("Repo Summary:")

            prompt = f"Summarize the following GitHub repository README content in a {Depth_Bar} manner:\n\n{readme_content}"
            tech_stack_prompt = f"Extract the tech stack used in the following README content:\n\n{readme_content}"

            llm_summary = generate(prompt)
            llm_tech_stack = generate(tech_stack_prompt)

            if llm_summary:
                st.text(llm_summary)
                st.subheader("Tech Stack:")
                st.text(llm_tech_stack or "Could not extract tech stack.")

                # ✅ SAVE so download button becomes enabled
                combined_report = (
                    f"Repo: {owner}/{repo_name}\n\n"
                    f"SUMMARY:\n{llm_summary}\n\n"
                    f"TECH STACK:\n{llm_tech_stack or ''}\n"
                )
                st.session_state.summary_text = combined_report
                
                download_slot.download_button(
                    "Download README Summary",
                    data=(st.session_state.get("summary_text") or ""),
                    file_name="repo_summary.txt",
                    disabled=(st.session_state.get("summary_text") is None),
                    key="download_summary_btn_enabled"
                )

            else:
                st.error("Failed to generate summary from LLM.")
    else:
        with results_container:
            st.warning("No README found or failed to fetch README.")
