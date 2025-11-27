from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from faker import Faker
import random
from users.models import User


class Command(BaseCommand):
    help = 'Create fake users for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of users to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']

        user_types = ['member', 'instructor', 'admin']
        weights = [0.85, 0.10, 0.05]  # 85% members, 10% instructors, 5% admins

        created_count = 0

        for i in range(count):
            try:
                user_type = random.choices(user_types, weights=weights)[0]
                username = fake.user_name()
                email = fake.email()

                while User.objects.filter(username=username).exists():
                    username = fake.user_name()
                while User.objects.filter(email=email).exists():
                    email = fake.email()

                _ = User.objects.create(
                    username=username,
                    email=email,
                    password=make_password('password123'),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type=user_type,
                    phone=fake.phone_number()[:20],
                    date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    health_notes=fake.sentence(nb_words=10) if random.random() < 0.3 else '',
                )

                created_count += 1

                if created_count % 10 == 0:
                    self.stdout.write(f'Created {created_count} users...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake users!')
        )
        self.stdout.write(
            self.style.WARNING('Default password for all users: "password123"')
        )
