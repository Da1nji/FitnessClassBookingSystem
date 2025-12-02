from django.core.management.base import BaseCommand
from faker import Faker
import random
from django.utils import timezone
from users.models import User
from classes.models import FitnessClass, Booking


class Command(BaseCommand):
    help = 'Create fake bookings for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=200,
            help='Number of bookings to create'
        )

    def handle(self, *args, **options):
        _ = Faker()
        count = options['count']

        users = User.objects.filter(user_type='member', is_active=True)
        fitness_classes = FitnessClass.objects.filter(is_active=True, is_cancelled=False)

        if not users.exists():
            self.stdout.write(self.style.ERROR('No member users found!'))
            return

        if not fitness_classes.exists():
            self.stdout.write(self.style.ERROR('No fitness classes found!'))
            return

        booking_statuses = ['pending', 'confirmed', 'cancelled', 'attended', 'no_show']
        status_weights = [0.2, 0.6, 0.1, 0.05, 0.05]

        created_count = 0

        for i in range(count):
            try:
                user = random.choice(users)
                fitness_class = random.choice(fitness_classes)

                # Skip if user already has a booking for this class
                if Booking.objects.filter(user=user, fitness_class=fitness_class).exists():
                    continue

                status = random.choices(booking_statuses, weights=status_weights)[0]

                booking = Booking.objects.create(
                    user=user,
                    fitness_class=fitness_class,
                    status=status,
                )

                # Set timestamps based on status
                if status in ['confirmed', 'attended']:
                    booking.is_email_confirmed = True
                    delta = timezone.timedelta(days=random.randint(0, 7))
                    booking.confirmed_at = timezone.now() - delta

                if status == 'cancelled':
                    delta = timezone.timedelta(days=random.randint(0, 3))
                    booking.cancelled_at = timezone.now() - delta
                booking.save()

                created_count += 1

                if created_count % 50 == 0:
                    self.stdout.write(f'Created {created_count} bookings...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating booking: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake bookings!')
        )
