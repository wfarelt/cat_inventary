from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Create standard groups and assign model permissions for the application.'

    def handle(self, *args, **options):
        # mapping: group -> [(app_label, model, perms...)]
        mapping = {
            'Admin': [
                ('products', 'product', ['add', 'change', 'delete', 'view']),
                ('products', 'category', ['add', 'change', 'delete', 'view']),
                ('products', 'brand', ['add', 'change', 'delete', 'view']),
                ('products', 'productkit', ['add', 'change', 'delete', 'view']),
                ('company', 'company', ['add', 'change', 'delete', 'view']),
                ('auth', 'user', ['add', 'change', 'delete', 'view']),
            ],
            'Manager': [
                ('products', 'product', ['add', 'change', 'view']),
                ('products', 'category', ['add', 'change', 'view']),
                ('products', 'brand', ['add', 'change', 'view']),
                ('products', 'productkit', ['add', 'change', 'view']),
                ('company', 'company', ['view', 'change']),
            ],
            'Clerk': [
                ('products', 'product', ['add', 'change', 'view']),
                ('products', 'brand', ['view']),
                ('products', 'productkit', ['view']),
            ],
            'Viewer': [
                ('products', 'product', ['view']),
                ('products', 'category', ['view']),
                ('products', 'brand', ['view']),
                ('products', 'productkit', ['view']),
                ('company', 'company', ['view']),
            ],
        }

        for group_name, rules in mapping.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created group: {group_name}'))
            for app_label, model, perms in rules:
                try:
                    ct = ContentType.objects.get(app_label=app_label, model=model)
                except ContentType.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'ContentType not found for {app_label}.{model}'))
                    continue
                for p in perms:
                    codename = f'{p}_{model}'
                    try:
                        perm = Permission.objects.get(content_type=ct, codename=codename)
                        group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Permission {codename} not found'))
            group.save()
        self.stdout.write(self.style.SUCCESS('Roles and permissions setup completed.'))
