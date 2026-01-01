"""DocuStruct parser: rules-based PDF structure extraction using PyMuPDF (fitz).

Strategy:
- Parse PDF page by page (streaming)
- Extract text spans with font size and font name
- Compute document-level font-size median to detect headings
- Use thresholds to map font sizes to H1/H2/H3
- Title: the largest text on page 0 (first page) usually
"""
from typing import List, Dict, Any
import statistics

try:
    import fitz  # PyMuPDF
except Exception as e:
    fitz = None

class ParseError(Exception):
    pass

def _extract_spans_from_page(page) -> List[Dict[str, Any]]:
    # returns spans with text, size, font, bbox, block_no
    data = page.get_text('dict')
    spans = []
    for bidx, block in enumerate(data.get('blocks', [])):
        if block.get('type') != 0:
            continue
        for line in block.get('lines', []):
            for span in line.get('spans', []):
                spans.append({
                    'text': span.get('text', '').strip(),
                    'size': span.get('size', 0),
                    'font': span.get('font', ''),
                    'bbox': span.get('bbox', []),
                    'block': bidx
                })
    return spans

def analyze_pdf_path(path: str, max_pages: int = None) -> Dict[str, Any]:
    if fitz is None:
        raise ParseError('PyMuPDF (fitz) is required. Install with: pip install PyMuPDF')

    doc = fitz.open(path)
    try:
        return analyze_document(doc, max_pages=max_pages)
    finally:
        doc.close()

def analyze_pdf_bytes(data: bytes, max_pages: int = None) -> Dict[str, Any]:
    if fitz is None:
        raise ParseError('PyMuPDF (fitz) is required. Install with: pip install PyMuPDF')
    doc = fitz.open(stream=data, filetype='pdf')
    try:
        return analyze_document(doc, max_pages=max_pages)
    finally:
        doc.close()

def analyze_document(doc, max_pages: int = None) -> Dict[str, Any]:
    total_pages = doc.page_count
    pages_to_process = range(total_pages) if max_pages is None else range(min(total_pages, max_pages))
    all_sizes = []
    page_spans = {}

    for pno in pages_to_process:
        page = doc.load_page(pno)
        spans = _extract_spans_from_page(page)
        page_spans[pno] = spans
        for s in spans:
            if s['text']:
                all_sizes.append(s['size'])

    if not all_sizes:
        return {'title': '', 'sections': [], 'stats': {'pages': total_pages, 'fonts': 0}}

    median_size = statistics.median(all_sizes)
    # define thresholds relative to median
    h1_thresh = median_size * 1.45
    h2_thresh = median_size * 1.2
    # produce sections
    sections = []
    for pno in pages_to_process:
        spans = page_spans.get(pno, [])
        # group contiguous spans by block and choose candidate headings
        for s in spans:
            text = s['text']
            if not text:
                continue
            size = s['size']
            # heuristic: headings are relatively larger than median and reasonably short
            if size >= h2_thresh and len(text) < 200:
                level = 'H3'
                if size >= h1_thresh:
                    level = 'H1'
                elif size >= h2_thresh:
                    level = 'H2'
                sections.append({
                    'level': level,
                    'text': text,
                    'page': pno + 1
                })
    # attempt to coalesce consecutive headings with same level and short distance
    consolidated = []
    prev = None
    for sec in sections:
        if prev and prev['level'] == sec['level'] and prev['page'] == sec['page']:
            # merge by appending text (rare)
            prev['text'] = prev['text'] + ' / ' + sec['text']
        else:
            consolidated.append(sec)
            prev = sec

    # Title heuristic: first large span on page 0
    title = ''
    if 0 in page_spans:
        page0_spans = [s for s in page_spans[0] if s['text']]
        if page0_spans:
            # pick largest size span
            largest = max(page0_spans, key=lambda x: x['size'])
            if largest['size'] >= median_size * 1.2 and len(largest['text']) < 200:
                title = largest['text']

    stats = {
        'pages': total_pages,
        'fonts': len(set([s['font'] for p in page_spans.values() for s in p])),
        'estimated_read_time': _estimate_read_time(page_spans)
    }

    return {
        'title': title,
        'sections': consolidated,
        'stats': stats
    }

def _estimate_read_time(page_spans: Dict[int, List[Dict[str, Any]]]) -> str:
    # crude read time estimate: words / 200 wpm
    total_words = 0
    for spans in page_spans.values():
        for s in spans:
            total_words += len(s['text'].split())
    minutes = max(1, int(total_words / 200))
    return f"{minutes} min"
