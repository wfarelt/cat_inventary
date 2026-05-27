from django.conf import settings


def is_admin(user):
    """Centralized admin check used for compatibility and quick checks.

    Returns True for active superusers, staff, or users in configured groups.
    """
    if not (user and getattr(user, 'is_active', False)):
        return False
    if getattr(user, 'is_superuser', False):
        return True
    if getattr(user, 'is_staff', False):
        return True
    allowed = getattr(settings, 'PRODUCTS_ALLOWED_GROUPS', ['Admin', 'Manager'])
    try:
        user_groups = set(user.groups.values_list('name', flat=True))
    except Exception:
        user_groups = set()
    return bool(user_groups.intersection(set(allowed)))
