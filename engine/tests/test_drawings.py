from opengrid.drawings import render_svg, export_drawing


def test_svg_contains_equipment(example):
    svg = render_svg(example)
    assert '<svg' in svg and 'MSB' in svg and 'BESS_500' in svg
    assert 'NOT FOR CONSTRUCTION' in svg


def test_svg_file(example, tmp_path):
    p = tmp_path / 'concept.svg'
    r = export_drawing(example, p)
    assert p.stat().st_size > 500
    assert r['approved'] is False


def test_dxf_file(example, tmp_path):
    __import__('pytest').importorskip('ezdxf')
    p = tmp_path / 'concept.dxf'
    export_drawing(example, p)
    assert p.stat().st_size > 500


def test_pdf_file(example, tmp_path):
    __import__('pytest').importorskip('cairosvg')
    p = tmp_path / 'concept.pdf'
    export_drawing(example, p)
    assert p.read_bytes().startswith(b'%PDF')
