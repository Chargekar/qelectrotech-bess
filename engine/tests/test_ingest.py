import json
from opengrid.ingest import ingest_pdf


def test_ingest_text_pdf(tmp_path):
    reportlab = __import__('pytest').importorskip('reportlab')
    from reportlab.pdfgen import canvas
    p = tmp_path / 'asbuilt.pdf'
    c = canvas.Canvas(str(p))
    c.drawString(50, 730, 'EXISTING ONE-LINE DIAGRAM PANEL 1, MSB-1, PCS-2')
    c.showPage();c.save()
    r = ingest_pdf(p, tmp_path/'evidence.json')
    data = json.loads((tmp_path/'evidence.json').read_text())
    assert r['review_required'] is True
    assert data['model_created'] is False
    assert data['page_count'] == 1
    assert data['pages'][0]['reviewed'] is False
