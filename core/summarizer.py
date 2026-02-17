from core.ollama_client import generate

def chunk_text(text, max_chars=6000):
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end

    return chunks


def summarize_file(path, content):
    chunks = chunk_text(content)
    chunk_summaries = []

    for chunk in chunks:
        prompt = f"""
Explain the purpose of this code chunk from file {path}.
Be concise.

Code:
{chunk}
"""
        summary = generate(prompt)
        if summary:
            chunk_summaries.append(summary)

    combined_prompt = f"""
Combine these summaries into one explanation
for file {path}:

{chr(10).join(chunk_summaries)}
"""

    final_summary = generate(combined_prompt)

    return {
        "file": path,
        "summary": final_summary
    }
