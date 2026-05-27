from django.db.models import Q
from .models import Product, Category


def parse_advanced_query(q: str):
    # Split by % and strip
    terms = [t.strip() for t in q.split('%') if t.strip()]
    return terms


def search_products(query: str, limit: int = 30):
    qs = Product.objects.select_related('category').filter(is_active=True)
    q = query.strip()
    if not q:
        return qs.none()

    # If contains %, do advanced split
    if '%' in q:
        terms = parse_advanced_query(q)
        for term in terms:
            term_q = Q(code__icontains=term) | Q(description__icontains=term) | Q(cross_reference__icontains=term) | Q(category__name__icontains=term)
            qs = qs.filter(term_q)
        return qs.order_by('code')[:limit]

    # Otherwise progressive matching: exact code, startswith code partials, description, cross_reference
    # exact code
    exact = qs.filter(code__iexact=q)
    if exact.exists():
        return exact.order_by('code')[:limit]

    # partial code
    partial = qs.filter(code__istartswith=q)
    if partial.exists():
        return partial.order_by('code')[:limit]

    # cross_reference and description
    others = qs.filter(Q(cross_reference__icontains=q) | Q(description__icontains=q) | Q(category__name__icontains=q))
    return others.order_by('code')[:limit]
