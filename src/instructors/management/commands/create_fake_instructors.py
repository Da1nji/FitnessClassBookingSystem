from django.core.management.base import BaseCommand
from faker import Faker
import random
from users.models import User
from instructors.models import Instructor


class Command(BaseCommand):
    help = 'Create fake instructors for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=15,
            help='Number of instructors to create'
        )

    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']

        instructor_users = User.objects.filter(user_type='instructor')[:count]

        if len(instructor_users) < count:
            self.stdout.write(
                self.style.WARNING(
                    f'Only found {
                        len(instructor_users)} users with instructor type. Creating more...')
            )
            from django.contrib.auth.hashers import make_password
            for i in range(count - len(instructor_users)):
                username = f"instructor_{fake.user_name()}"
                while User.objects.filter(username=username).exists():
                    username = f"instructor_{fake.user_name()}"

                user = User.objects.create(
                    username=username,
                    email=fake.email(),
                    password=make_password('password123'),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    user_type='instructor',
                    phone=fake.phone_number()[:20],
                )
                instructor_users = list(instructor_users) + [user]

        created_count = 0

        for user in instructor_users:
            try:

                _ = Instructor.objects.create(
                    user=user,
                    bio=fake.paragraph(nb_sentences=3),
                    is_active=random.random() < 0.9,  # 90% active
                )

                created_count += 1
                self.stdout.write(f'Created instructor: {user.get_full_name()}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating instructor for user {user.username}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake instructors!')
        )
