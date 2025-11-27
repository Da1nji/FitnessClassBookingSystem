from django.core.management.base import BaseCommand
from faker import Faker
import random
from datetime import timedelta
from django.utils import timezone
from classes.models import FitnessClass, ClassType, Level
from instructors.models import Instructor


class Command(BaseCommand):
    help = 'Create fake fitness classes for demo purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of fitness classes to create'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=60,
            help='Number of days in the future to schedule classes'
        )

    def handle(self, *args, **options):
        count = options['count']
        days = options['days']

        class_types = ClassType.objects.filter(is_active=True)
        levels = Level.objects.filter()
        instructors = Instructor.objects.filter(is_active=True)

        if not class_types.exists():
            self.stdout.write(
                self.style.ERROR('No class types found. Run create_fake_class_data first!')
            )
            return

        if not levels.exists():
            self.stdout.write(
                self.style.ERROR('No levels found. Run create_fake_class_data first!')
            )
            return

        if not instructors.exists():
            self.stdout.write(
                self.style.ERROR('No instructors found. Run create_fake_instructors first!')
            )
            return

        created_count = 0

        for i in range(count):
            try:
                class_type = random.choice(class_types)
                level = random.choice(levels)
                instructor = random.choice(instructors) if random.random(
                ) < 0.9 else None  # 90% have instructors

                start_days = random.randint(0, days)
                start_hour = random.choice([6, 7, 8, 9, 10, 16, 17, 18, 19, 20])
                start_minute = random.choice([0, 15, 30, 45])

                start_time = timezone.now() + timedelta(days=start_days,
                                                        hours=start_hour, minutes=start_minute)

                # Duration: 30, 45, 60, 75, or 90 minutes
                duration = random.choice([30, 45, 60, 75, 90])
                end_time = start_time + timedelta(minutes=duration)

                # Price: free, or between $10 and $50
                price = 0 if random.random() < 0.2 else random.randint(10, 50)

                # Capacity: between 5 and 30
                max_capacity = random.choice([5, 10, 15, 20, 25, 30])

                _ = FitnessClass.objects.create(
                    class_type=class_type,
                    level=level,
                    instructor=instructor,
                    duration_minutes=duration,
                    max_capacity=max_capacity,
                    price=price,
                    start_time=start_time,
                    end_time=end_time,
                    is_active=random.random() < 0.9,  # 90% active
                    is_cancelled=random.random() < 0.05,  # 5% cancelled
                )

                created_count += 1

                if created_count % 20 == 0:
                    self.stdout.write(f'Created {created_count} classes...')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating class: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} fake fitness classes!')
        )
