from io import BytesIO

from django.conf import settings


def render_pdf_from_html(html: str) -> bytes:
    """Render PDF bytes from HTML string using WeasyPrint if available.
    Raises Exception if PDF generation not possible.
    """
    try:
        from weasyprint import HTML
    except Exception as e:
        raise RuntimeError('WeasyPrint not available: install weasyprint to enable PDF generation') from e

    out = BytesIO()
    HTML(string=html).write_pdf(out)
    return out.getvalue()
