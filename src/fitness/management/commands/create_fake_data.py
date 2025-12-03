from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Create all fake data for the fitness booking system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create'
        )
        parser.add_argument(
            '--instructors',
            type=int,
            default=15,
            help='Number of instructors to create'
        )
        parser.add_argument(
            '--classes',
            type=int,
            default=100,
            help='Number of fitness classes to create'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting fake data generation...'))

        self.stdout.write('Creating class types and levels...')
        call_command('create_fake_class_data')

        self.stdout.write(f'Creating {options["users"]} users...')
        call_command('create_fake_users', count=options['users'])

        self.stdout.write(f'Creating {options["instructors"]} instructors...')
        call_command('create_fake_instructors', count=options['instructors'])

        self.stdout.write(f'Creating {options["classes"]} fitness classes...')
        call_command('create_fake_classes', count=options['classes'])

        self.stdout.write(self.style.SUCCESS('All fake data created successfully!'))
        self.stdout.write(self.style.WARNING('Default password for all users: "password123"'))
        self.stdout.write(self.style.SUCCESS('Your demo database is now ready!'))
