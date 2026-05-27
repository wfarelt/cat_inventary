from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from sales.models import Sale, SaleStatus
from sales import services as sales_services


class Command(BaseCommand):
    help = 'Expire reservations: release stock_reserved for Sales with status RESERVA and expiration_date <= today'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not perform changes, only show what would be done')
        parser.add_argument('--limit', type=int, default=0, help='Limit number of reservations to process (0 = no limit)')
        parser.add_argument('--date', type=str, help='Use a specific date (YYYY-MM-DD) instead of today')

    def handle(self, *args, **options):
        dry = options.get('dry_run')
        limit = options.get('limit') or 0
        date_opt = options.get('date')

        if date_opt:
            try:
                today = timezone.datetime.strptime(date_opt, '%Y-%m-%d').date()
            except Exception as e:
                raise CommandError(f'Invalid date format: {e}')
        else:
            today = timezone.localdate()

        qs = Sale.objects.filter(status=SaleStatus.RESERVA, expiration_date__isnull=False, expiration_date__lte=today).order_by('expiration_date')
        total = qs.count()
        if limit and limit > 0:
            qs = qs[:limit]

        self.stdout.write(self.style.NOTICE(f'Found {total} expired reservations (processing {qs.count()}) as of {today}'))

        processed = 0
        for sale in qs:
            self.stdout.write(f'Processing Sale #{sale.number or sale.pk} (expires {sale.expiration_date})...')
            if dry:
                self.stdout.write('DRY RUN: would release reservation and mark ANULADO')
                processed += 1
                continue
            try:
                sales_services.release_reservation(sale, user=None, ip=None, reason='Reservation expired (management command)')
                self.stdout.write(self.style.SUCCESS(f'Released reservation for sale {sale.number or sale.pk}'))
                processed += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error processing sale {sale.pk}: {e}'))

        self.stdout.write(self.style.NOTICE(f'Done. Processed {processed} reservations.'))