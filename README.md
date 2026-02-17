# RepoMind
### RepoMind is a Streamlit-based application that analyzes a GitHub repository and generates an easy-to-understand explanation using a local LLM (Meta Llama 2 via Ollama).

## To try it out
### clone repo in any place using
``` bash
git clone https://github.com/Hiiammister/RepoMind
```

#Few Pre-requisites for it to run properly
## 1. Install Python
```bash
python --version
```
## 2. Install Git
```bash
git --version
```
## 3. Install Ollama + Llama 2
### Install Ollama from official site: https://ollama.com/download

## 4. Pull LLama2 model (while in terminal/ Powershell)
```bash
ollama pull llama2
```
### Test Model:
```bash
ollama run llama2
```
### Exit by:
```bash
/bye
```
# Project Setup
## 1. Open Terminal/ Powershell
## 2. Install Dependencies
```bash
pip install streamlit
```
## 2. Locate and Change to project folder
```bash
cd RepoMind
```
# Run the Project by:
```bash
streamlit run [file_name.py]
#in this case, streamlit run app.py
```







