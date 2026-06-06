from django.db import migrations


def forwards(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    try:
        ct = ContentType.objects.get(app_label='products', model='brand')
    except ContentType.DoesNotExist:
        return

    perms = Permission.objects.filter(content_type=ct, codename__in=['add_brand', 'change_brand', 'delete_brand', 'view_brand'])
    if not perms.exists():
        return

    for group_name, codenames in {
        'Admin': ['add_brand', 'change_brand', 'delete_brand', 'view_brand'],
        'Manager': ['add_brand', 'change_brand', 'view_brand'],
        'Clerk': ['view_brand'],
        'Viewer': ['view_brand'],
    }.items():
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        group.permissions.add(*perms.filter(codename__in=codenames))


def backwards(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')

    try:
        ct = ContentType.objects.get(app_label='products', model='brand')
    except ContentType.DoesNotExist:
        return

    perms = Permission.objects.filter(content_type=ct, codename__in=['add_brand', 'change_brand', 'delete_brand', 'view_brand'])
    for group_name in ['Admin', 'Manager', 'Clerk', 'Viewer']:
        try:
            group = Group.objects.get(name=group_name)
        except Group.DoesNotExist:
            continue
        group.permissions.remove(*perms)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_brand_brand_ref'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
