from core.ollama_client import generate

def synthesize_report(file_summaries):
    summaries_text = "\n\n".join(
        f"{f['file']}:\n{f['summary']}"
        for f in file_summaries
    )

    prompt = f"""
Using these file summaries, explain the repository:

Provide:
1. Project overview
2. Tech stack
3. Architecture explanation
4. How components interact
5. Resume-ready summary

Summaries:
{summaries_text}
"""

    return generate(prompt)




def chunk_text(text, max_chars=6000):
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end

    return chunks
