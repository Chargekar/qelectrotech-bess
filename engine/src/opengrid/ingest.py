"""Conservative PDF ingestion: evidence first, NO inferred circuit topology.

Scanned drawings are untrusted documents; OCR text is not verified design data.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


# Initial hints only. These are NOT interpreted equipment or connections.
TAG_PATTERN = re.compile(r"\b(?:MSB|MDB|MCC|PANEL|INV|BESS|PCS|XFMR|CB|PV|SWGR)[-_ ]?\d*[A-Z]?\b", re.I)


def ingest_pdf(path: Path, output: Path, *, max_pages: int = 30) -> dict:
    path = Path(path)
    output = Path(output)
    if path.suffix.lower() != '.pdf' or not path.is_file():
        raise ValueError('Input must be an existing PDF file')
    if path.stat().st_size > 50 * 1024 * 1024:
        raise ValueError('PDF larger than 50 MiB; split or review separately')
    try:
        import pdfplumber
    except ImportError as exc:
        raise RuntimeError('PDF ingest requires pip install ".[ingest]"') from exc
    source_sha = hashlib.sha256(path.read_bytes()).hexdigest()
    pages = []
    with pdfplumber.open(path) as pdf:
        if len(pdf.pages) > max_pages:
            raise ValueError(f'PDF contains {len(pdf.pages)} pages; per-ingest limit {max_pages}')
        for index, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ''
            extraction = 'embedded_text'
            warnings = []
            if len(text.strip()) < 25:
                extraction = 'ocr'
                if not shutil.which('tesseract'):
                    extraction = 'unavailable'
                    warnings.append('Tesseract not installed; scanned page text not extracted')
                else:
                    try:
                        import pypdfium2 as pdfium
                        with tempfile.TemporaryDirectory(prefix='og-ocr-') as tempdir:
                            # Render only the selected page; 2x scale gives ~144 dpi.
                            pdfium_doc = pdfium.PdfDocument(str(path))
                            try:
                                bitmap = pdfium_doc[index-1].render(scale=2.0)
                                img = Path(tempdir)/'page.png'
                                bitmap.to_pil().save(img)
                            finally:
                                pdfium_doc.close()
                            result = subprocess.run(
                                ['tesseract', str(img), 'stdout'], capture_output=True,
                                text=True, check=True, timeout=90,
                            )
                            text = result.stdout
                    except (subprocess.SubprocessError, Exception) as exc:
                        # OCR failure must not cause guessing. Preserve the failed stage.
                        extraction = 'failed'
                        warnings.append(f'OCR unsuccessful: {type(exc).__name__}')
            pages.append({
                'page': index,
                'method': extraction,
                'text': text,
                'candidate_tags': sorted(set(TAG_PATTERN.findall(text)), key=str.casefold),
                'warnings': warnings,
                'reviewed': False,
            })
    report = {
        'source_file': path.name,
        'source_sha256': source_sha,
        'page_count': len(pages),
        'model_created': False,
        'requires_engineer_review': True,
        'limitations': [
            'Text and tags are extraction candidates, not verified electrical data',
            'No symbol recognition or graph reconstruction is implemented in this release',
            'No existing vs proposed classification is inferred from OCR',
        ],
        'pages': pages,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return {'manifest': str(output), 'page_count': len(pages), 'review_required': True}
