def select_files(tree, max_files=35, include_tests=False, include_docs=False):
    """
    tree: list[str] of file paths (from get_repo_tree)
    returns: list[str] selected file paths
    """

    ALWAYS_INCLUDE = {
        "README.md", "README.MD", "readme.md",
        "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
        "requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock",
        "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
        "Makefile",
        ".env.example", ".env.template",
        "tsconfig.json", "vite.config.js", "vite.config.ts",
        "next.config.js", "next.config.mjs",
    }

    AVOID_CONTAINS = [
        "node_modules/", "dist/", "build/", ".next/", ".venv/", "venv/",
        "__pycache__/", ".git/", "coverage/", ".pytest_cache/"
    ]

    PREFER_PREFIX = [
        "src/", "app/", "backend/", "server/", "api/", "services/", "lib/"
    ]

    TEST_DOC_HINTS = ["test", "tests", "__tests__", "spec", "docs", "doc", "documentation"]

    def should_avoid(path: str) -> bool:
        return any(bad in path for bad in AVOID_CONTAINS)

    def is_test_or_doc(path: str) -> bool:
        p = path.lower()
        return any(h in p for h in TEST_DOC_HINTS)

    def score(path: str) -> int:
        p = path.lower()
        s = 0

        # Prefer important roots
        if any(p.startswith(pref) for pref in PREFER_PREFIX):
            s += 50

        # Prefer typical entry points
        name = p.split("/")[-1]
        if name in {"main.py", "app.py", "server.py", "index.js", "index.ts", "main.ts", "main.js", "app.tsx", "index.tsx"}:
            s += 40

        # Prefer config/deps/readme
        if path in ALWAYS_INCLUDE or name in {x.lower() for x in ALWAYS_INCLUDE}:
            s += 100

        # Penalize tests/docs if toggles off
        if is_test_or_doc(path):
            if not include_tests and ("test" in p or "spec" in p):
                s -= 60
            if not include_docs and ("docs" in p or "/doc" in p):
                s -= 60

        # Light preference for common code files
        if any(p.endswith(ext) for ext in [".py", ".js", ".ts", ".tsx", ".java", ".go", ".rb", ".php"]):
            s += 10

        return s

    # Filter out junk
    candidates = [p for p in tree if not should_avoid(p)]

    # Always include first (if present in repo)
    selected = []
    lower_tree = {p.lower(): p for p in candidates}
    for item in ALWAYS_INCLUDE:
        if item.lower() in lower_tree:
            selected.append(lower_tree[item.lower()])

    # Score the rest and fill up to max_files
    remaining = [p for p in candidates if p not in selected]
    remaining_sorted = sorted(remaining, key=score, reverse=True)

    for p in remaining_sorted:
        if len(selected) >= max_files:
            break
        selected.append(p)

    # De-dup, preserve order
    seen = set()
    final = []
    for p in selected:
        if p not in seen:
            seen.add(p)
            final.append(p)

    return final
