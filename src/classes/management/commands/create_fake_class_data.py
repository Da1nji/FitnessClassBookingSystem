from django.core.management.base import BaseCommand
from classes.models import ClassType, Level


class Command(BaseCommand):
    help = 'Create initial class types and levels'

    def handle(self, *args, **options):
        class_types_data = [
            {'name': 'Yoga', 'description': (
                'Mind-body practice combining physical postures, breathing exercises, '
                'and meditation'
            )},
            {'name': 'Pilates', 'description': ('Exercise method that focuses on core strength,'
                                                ' flexibility, and body awareness')},
            {'name': 'Cardio', 'description': ('High-energy workouts focused on'
                                               'improving cardiovascular health')},
            {'name': 'Strength Training',
             'description': 'Workouts designed to build muscle strength and endurance'},
            {'name': 'Dance',
             'description': 'Fun, rhythm-based workouts combining dance moves with fitness'},
            {'name': 'Martial Arts',
             'description': 'Self-defense techniques combined with physical conditioning'},
            {'name': 'Cycling',
             'description': 'Indoor cycling classes for cardio and leg strength'},
            {'name': 'HIIT',
             'description': 'High-Intensity Interval Training for maximum calorie burn'},
            {'name': 'Boxing',
             'description': 'High-intensity boxing workouts for cardio and strength'},
            {'name': 'Meditation',
             'description': 'Mindfulness and relaxation techniques for stress reduction'},
            {'name': 'Zumba',
             'description': 'Dance fitness party with Latin and international music'},
            {'name': 'Barre',
             'description': 'Ballet-inspired workout focusing on small, isometric movements'},
        ]

        levels_data = [
            {'name': 'Beginner',
             'description': 'Perfect for those new to fitness or specific class types',
             'difficulty_order': 1},
            {'name': 'Intermediate',
             'description': 'For those with some experience looking to challenge themselves',
             'difficulty_order': 2},
            {'name': 'Advanced',
             'description': 'High-intensity classes for experienced fitness enthusiasts',
             'difficulty_order': 3},
            {'name': 'All Levels',
             'description': 'Suitable for everyone, with modifications provided',
             'difficulty_order': 4},
            {'name': 'Kids',
             'description': 'Classes designed specifically for children',
             'difficulty_order': 5},
        ]

        class_type_count = 0
        for type_data in class_types_data:
            _, created = ClassType.objects.get_or_create(
                name=type_data['name'],
                defaults=type_data
            )
            if created:
                class_type_count += 1
                self.stdout.write(f'Created class type: {type_data["name"]}')

        level_count = 0
        for level_data in levels_data:
            _, created = Level.objects.get_or_create(
                name=level_data['name'],
                defaults=level_data
            )
            if created:
                level_count += 1
                self.stdout.write(f'Created level: {level_data["name"]}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {
                               class_type_count} class types and {level_count} levels!')
        )
