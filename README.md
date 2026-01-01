# DocuStruct — Offline Document Structure & Analysis Engine

DocuStruct extracts structured outlines (Title, H1, H2, H3) and document metadata from PDFs **offline** using deterministic layout heuristics (no ML models). It provides:

- CLI (`docustruct analyze`)
- REST API (FastAPI)
- Dockerfile for deployment
- Benchmarks script

## Features (minimal)
- JSON outline (title + sections with level and page)
- Metadata: pages, fonts, estimated read time
- Streaming parsing (page-by-page) to limit memory
- Deterministic rule-based headings detection (font sizes & spacing)

## Quickstart (development)
1. Create virtualenv and install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. CLI usage:
```bash
python -m docustruct.cli analyze sample.pdf --out outline.json
```

3. Run API locally:
```bash
uvicorn docustruct.api:app --host 0.0.0.0 --port 8080 --reload
# then POST /analyze with form file
```

4. Docker:
```bash
docker build -t docustruct:latest .
docker run -p 8080:8080 --rm docustruct:latest
```

## Benchmarks
See `bench/bench.sh`. Targets:
- 50-page PDF: < 10s
- Memory usage: < 200 MB
- Cold start: < 2s
- Model size: 0 MB

## Project layout
```
docustruct/
└─ src/docustruct/
   ├─ __init__.py
   ├─ parser.py
   ├─ cli.py
   └─ api.py
Dockerfile
requirements.txt
bench/bench.sh
README.md
```

## Implementation notes
- This project uses PyMuPDF (package name `PyMuPDF`, import `fitz`) for parsing PDFs.
- The heading detection is rules-based using font-size statistics and positional heuristics.
- If you cannot install `PyMuPDF` locally, the code will give a clear error message.

