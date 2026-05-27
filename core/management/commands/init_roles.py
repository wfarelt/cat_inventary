from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Create initial groups/roles for the ERP'

    def handle(self, *args, **options):
        roles = ['Administrator', 'Sales', 'Accounting', 'Warehouse']
        for r in roles:
            group, created = Group.objects.get_or_create(name=r)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group {r}'))
            else:
                self.stdout.write(f'Group {r} already exists')

        # Example: assign basic permissions for User model to Administrator
        try:
            ct = ContentType.objects.get(app_label='auth', model='user')
            perms = Permission.objects.filter(content_type=ct)
            admin = Group.objects.get(name='Administrator')
            admin.permissions.set(perms)
            self.stdout.write(self.style.SUCCESS('Assigned auth.User perms to Administrator'))
        except ContentType.DoesNotExist:
            self.stdout.write('auth.User content type not found; skipping permission assignment')

        self.stdout.write(self.style.SUCCESS('Roles initialized'))
