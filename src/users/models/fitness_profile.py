from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class FitnessProfile(models.Model):
    """
    Detailed fitness profile for personalized workout recommendations
    """
    GOAL_CHOICES = [
        ('weight_loss', 'Weight Loss'),
        ('muscle_gain', 'Muscle Gain'),
        ('endurance', 'Endurance Improvement'),
        ('strength', 'Strength Building'),
        ('flexibility', 'Flexibility'),
        ('rehabilitation', 'Rehabilitation'),
        ('general_fitness', 'General Fitness'),
        ('sports_performance', 'Sports Performance'),
    ]

    ACTIVITY_LEVEL_CHOICES = [
        ('light', 'Light (exercise 1-3 days/week)'),
        ('moderate', 'Moderate (exercise 3-5 days/week)'),
        ('active', 'Active (exercise 6-7 days/week)'),
        ('very_active', 'Very Active (hard exercise 6-7 days/week)'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('beginner', 'Beginner (< 6 months)'),
        ('intermediate', 'Intermediate (6 months - 2 years)'),
        ('advanced', 'Advanced (> 2 years)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='fitness_profile'
    )

    height_cm = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(50), MaxValueValidator(250)]
    )
    weight_kg = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(20), MaxValueValidator(300)]
    )

    bmi = models.FloatField(null=True, blank=True, editable=False)
    bmi_category = models.CharField(max_length=20, blank=True, editable=False)

    primary_goal = models.CharField(
        max_length=50,
        choices=GOAL_CHOICES,
        default='general_fitness'
    )

    activity_level = models.CharField(
        max_length=20,
        choices=ACTIVITY_LEVEL_CHOICES,
        default='moderate'
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default='beginner'
    )
    months_experience = models.PositiveIntegerField(default=0)

    preferred_class_types = models.ManyToManyField(
        'classes.ClassType',
        blank=True,
        related_name='user_preferences'
    )
    preferred_times = models.JSONField(
        default=list,
        help_text="Preferred workout times (e.g., ['morning', 'evening'])"
    )

    has_injuries = models.BooleanField(default=False)
    injuries_description = models.TextField(blank=True)
    medical_conditions = models.TextField(blank=True)

    home_equipment = models.JSONField(
        default=list,
        help_text="List of equipment available at home"
    )

    preferred_duration_min = models.PositiveIntegerField(
        default=45,
        validators=[MinValueValidator(15), MaxValueValidator(180)]
    )
    days_per_week = models.PositiveIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    preferences_history = models.JSONField(
        default=list,
        help_text="Historical preferences and adjustments"
    )
    llm_prompt_context = models.TextField(
        blank=True,
        help_text="Cached prompt context for LLM"
    )

    last_workout_date = models.DateField(null=True, blank=True)
    workout_streak = models.PositiveIntegerField(default=0)
    total_workouts = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_llm_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Fitness Profile - {self.user.username}"

    class Meta:
        db_table = 'fitness_profiles'
        verbose_name = 'Fitness Profile'
        verbose_name_plural = 'Fitness Profiles'

    def save(self, *args, **kwargs):
        if self.height_cm and self.weight_kg:
            self.bmi = self.calculate_bmi()
            self.bmi_category = self.get_bmi_category()

        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new or 'update_fields' not in kwargs:
            self.update_llm_context()
            if not is_new:
                super().save(update_fields=['llm_prompt_context', 'updated_at'])

    def calculate_bmi(self):
        """Calculate Body Mass Index"""
        if self.height_cm > 0:
            height_m = self.height_cm / 100
            return round(self.weight_kg / (height_m ** 2), 1)
        return None

    def get_bmi_category(self):
        """Get BMI category based on calculated BMI"""
        if not self.bmi:
            return ""

        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 25:
            return "Normal"
        elif 25 <= self.bmi < 30:
            return "Overweight"
        else:
            return "Obese"

    def update_llm_context(self):
        """Generate prompt context for LLM"""
        context_parts = [
            f"User Profile for {self.user.get_full_name() or self.user.username}",
            f"Primary Goal: {self.get_primary_goal_display()}",
            f"Experience Level: {
                self.get_experience_level_display()} ({
                self.months_experience} months)",
            f"Activity Level: {self.get_activity_level_display()}",
            f"BMI: {self.bmi or 'Not calculated'} ({self.bmi_category})",
            f"Height: {
                self.height_cm} cm, Weight: {
                self.weight_kg} kg" if self.height_cm and self.weight_kg else "No height/weight",
            f"Workout Frequency: {
                self.days_per_week} days/week, {self.preferred_duration_min} minutes/session",
        ]

        if self.has_injuries and self.injuries_description:
            context_parts.append(f"Injuries: {self.injuries_description}")

        if self.medical_conditions:
            context_parts.append(f"Medical Conditions: {self.medical_conditions}")

        if self.pk and self.preferred_class_types.exists():
            class_types = ", ".join([ct.name for ct in self.preferred_class_types.all()])
            context_parts.append(f"Preferred Class Types: {class_types}")

        if self.home_equipment:
            equipment = ", ".join(self.home_equipment)
            context_parts.append(f"Available Equipment: {equipment}")

        self.llm_prompt_context = "\n".join(context_parts)

    @property
    def is_complete(self):
        """Check if profile is sufficiently complete for LLM recommendations"""
        required_fields = [
            self.primary_goal,
            self.activity_level,
            self.experience_level,
        ]
        return all(required_fields) and self.height_cm and self.weight_kg
