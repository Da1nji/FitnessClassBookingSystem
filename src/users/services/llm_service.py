import json
import anthropic
from django.conf import settings
from django.utils import timezone


class WorkoutLLMService:
    """Service for generating personalized workouts using LLM"""

    @staticmethod
    def generate_workout_plan(profile, days=7):
        """Generate a personalized workout plan using Anthropic Claude"""

        if not profile.is_complete:
            return {
                'error': 'Profile incomplete',
                'missing_fields': [
                    'height_cm' if not profile.height_cm else None,
                    'weight_kg' if not profile.weight_kg else None,
                    'primary_goal' if not profile.primary_goal else None,
                ]
            }

        # Shorter, more efficient prompt to save tokens
        prompt = f"""Create a {days}-day workout plan (JSON only, no markdown):

User: {profile.user.username}
Goal: {profile.get_primary_goal_display()}
Level: {profile.get_experience_level_display()}
BMI: {profile.bmi} ({profile.bmi_category})
Frequency: {profile.days_per_week} days/week, {profile.preferred_duration_min} min/session
Equipment: {', '.join(profile.home_equipment[:5]) if profile.home_equipment else 'Bodyweight only'}
{f' Injuries: {profile.injuries_description}' if profile.has_injuries else ''}

Return ONLY this JSON structure (no explanation):
{{
  "days": [
    {{
      "day": 1,
      "focus": "Upper Body",
      "exercises": [
        {{"name": "Push-ups", "sets": 3, "reps": "10-12", "rest": "60s"}}
      ],
      "duration": 30
    }}
  ],
  "tips": ["tip1", "tip2"],
  "warnings": ["warning1"]
}}"""

        try:
            # Use the FREE Haiku model (much cheaper than Sonnet)
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,  # Reduced tokens = lower cost
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            response_text = message.content[0].text.strip()

            # Clean up response (remove markdown if present)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()

            workout_plan = json.loads(response_text)

            profile.last_llm_update = timezone.now()
            profile.save()

            return workout_plan

        except anthropic.APIError as e:
            error_msg = str(e)

            # Handle rate limits gracefully
            if 'rate_limit' in error_msg.lower():
                return WorkoutLLMService._generate_fallback_plan(profile, days)

            return {
                'error': 'API error',
                'details': error_msg,
                'fallback': 'Try the /recommendations/ endpoint instead'
            }

        except json.JSONDecodeError as e:
            return {
                'error': 'Failed to parse response',
                'details': str(e),
                'raw': response_text[:200]
            }

        except Exception as e:
            return {
                'error': 'Unexpected error',
                'details': str(e)
            }

    @staticmethod
    def _generate_fallback_plan(profile, days):
        """Free fallback plan when API is unavailable"""

        goal_exercises = {
            'weight_loss': {
                'exercises': ['Jumping Jacks', 'Burpees', 'Mountain Climbers', 'High Knees'],
                'focus': 'High-intensity cardio'
            },
            'muscle_gain': {
                'exercises': ['Push-ups', 'Squats', 'Lunges', 'Plank'],
                'focus': 'Strength and resistance'
            },
            'endurance': {
                'exercises': ['Running', 'Jump Rope', 'Cycling', 'Swimming'],
                'focus': 'Cardiovascular endurance'
            },
            'flexibility': {
                'exercises': ['Yoga Flow', 'Dynamic Stretching', 'Pilates', 'Foam Rolling'],
                'focus': 'Flexibility and mobility'
            },
        }

        goal_data = goal_exercises.get(
            profile.primary_goal,
            goal_exercises['muscle_gain']
        )

        workouts = []
        for day in range(1, days + 1):
            # Rest day every 3-4 days
            if day % 4 == 0:
                workouts.append({
                    "day": day,
                    "focus": "Active Recovery",
                    "exercises": [
                        {"name": "Light Walking", "sets": 1, "reps": "20-30 min", "rest": "N/A"},
                        {"name": "Stretching", "sets": 1, "reps": "10-15 min", "rest": "N/A"}
                    ],
                    "duration": 30
                })
            else:
                exercises = []
                for i, ex in enumerate(goal_data['exercises'][:3]):
                    exercises.append({
                        "name": ex,
                        "sets": 3 if profile.experience_level != 'beginner' else 2,
                        "reps": "12-15" if profile.primary_goal == 'weight_loss' else "8-12",
                        "rest": "60s"
                    })

                workouts.append({
                    "day": day,
                    "focus": goal_data['focus'],
                    "exercises": exercises,
                    "duration": profile.preferred_duration_min
                })

        return {
            "days": workouts,
            "tips": [
                "Warm up for 5-10 minutes before each workout",
                "Focus on proper form over speed",
                "Stay hydrated throughout your workout",
                f"Rest adequately between sets ({profile.experience_level} level)"
            ],
            "warnings": [
                "Stop if you feel pain (not discomfort)",
                f"Consider your {profile.bmi_category} BMI when selecting intensity"
            ] + ([f"Mind your injuries: {profile.injuries_description}"]
                 if profile.has_injuries else []),
            "note": "This is a basic plan. Upgrade to premium for AI-personalized workouts."
        }

    @staticmethod
    def generate_class_recommendations(profile):
        """Generate class recommendations - lightweight version"""

        # Simple rule-based system (no API calls needed)
        goal_to_classes = {
            'weight_loss': ['HIIT', 'Cardio', 'Cycling', 'Boxing'],
            'muscle_gain': ['Strength Training', 'CrossFit', 'Functional Fitness'],
            'endurance': ['Cardio', 'Cycling', 'Running Club'],
            'flexibility': ['Yoga', 'Pilates', 'Stretching'],
            'general_fitness': ['All Levels', 'Circuit Training', 'Bootcamp']
        }

        recommended = goal_to_classes.get(profile.primary_goal, ['All Levels'])

        return {
            "recommended_class_types": recommended[:3],
            "weekly_frequency": profile.days_per_week,
            "optimal_times": (profile.preferred_times if profile.preferred_times
                              else ["morning", "evening"]),
            "avoid": ["high-impact exercises"] if profile.has_injuries else [],
            "rationale": (f"Based on your {profile.get_primary_goal_display()}"
                          "goal and {profile.get_experience_level_display()} level")
        }
