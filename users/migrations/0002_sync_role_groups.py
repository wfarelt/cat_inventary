from django.db import migrations


ROLE_TO_GROUP = {
    'admin': 'Admin',
    'sales': 'Clerk',
    'accounting': 'Viewer',
    'warehouse': 'Manager',
}


def forwards(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Group = apps.get_model('auth', 'Group')

    for group_name in set(ROLE_TO_GROUP.values()):
        Group.objects.get_or_create(name=group_name)

    for user in User.objects.all():
        group_name = ROLE_TO_GROUP.get(getattr(user, 'role', None))
        if not group_name:
            continue
        group = Group.objects.filter(name=group_name).first()
        if group is not None:
            user.groups.add(group)


def backwards(apps, schema_editor):
    User = apps.get_model('users', 'User')
    Group = apps.get_model('auth', 'Group')

    for user in User.objects.all():
        group_name = ROLE_TO_GROUP.get(getattr(user, 'role', None))
        if not group_name:
            continue
        group = Group.objects.filter(name=group_name).first()
        if group is not None:
            user.groups.remove(group)


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]