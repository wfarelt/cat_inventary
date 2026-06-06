# Roles & Permissions Matrix

This document describes recommended roles, groups and permission mappings for Cat Inventary (Phase 1 & 2).

## Roles (suggested)
- Admin: full access to everything (create/manage users, companies, products, categories, kits, imports).
- Manager: create/change products, categories, kits; view companies; no user management.
- Clerk: day-to-day product editing, limited to add/change/view products and view kits.
- Viewer: read-only access to products, categories, kits and companies.

## Suggested Django groups and permissions

- `Admin`:
  - products.product: add/change/delete/view
  - products.category: add/change/delete/view
  - products.productkit: add/change/delete/view
  - company.company: add/change/delete/view
  - auth.user: add/change/delete/view

- `Manager`:
  - products.product: add/change/view
  - products.category: add/change/view
  - products.productkit: add/change/view
  - company.company: view/change

- `Clerk`:
  - products.product: add/change/view
  - products.productkit: view

- `Viewer`:
  - products.product: view
  - products.category: view
  - products.productkit: view
  - company.company: view

## User role mapping

- `admin` -> `Admin`
- `sales` -> `Clerk`
- `accounting` -> `Viewer`
- `warehouse` -> `Manager`

Assign users to these groups so Django permissions and the UI stay aligned with the role field.

## How to apply
1. Run the management command to create groups and assign permissions:

```bash
python manage.py setup_roles
```

2. Assign users to groups via Django admin or using the shell.

## Notes & next steps
- Extend the mapping to include finer-grained domain permissions (e.g., import access, image management) by creating custom permissions on relevant models or separate boolean flags on groups.
- Add tests for permission enforcement on critical views (import, image upload, kit edit).
- Consider centralizing `is_admin` checks and replacing per-view `user_passes_test` with `@permission_required` where appropriate.
