"""Core business logic for ACEest Fitness & Gym.

This module has no Flask code, so every function can be unit tested on its own.
The rules are ported from the earlier desktop versions of ACEest (v1.1.2 to v3.2.4).
"""
import random
from datetime import date

# Program catalogue (from v1.1.2). calorie_factor = calories per kg of body weight.
PROGRAMS = {
    "FL": {
        "name": "Fat Loss",
        "workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
        "diet": "Egg Whites, Chicken, Fish Curry",
        "calorie_factor": 22,
    },
    "MG": {
        "name": "Muscle Gain",
        "workout": "Squat, Bench, Deadlift, Press, Rows",
        "diet": "Eggs, Biryani, Mutton Curry",
        "calorie_factor": 35,
    },
    "BG": {
        "name": "Beginner",
        "workout": "Air Squats, Ring Rows, Push-ups",
        "diet": "Balanced Tamil Meals",
        "calorie_factor": 26,
    },
}

# Templates used by the program generator (from v3.2.4).
PROGRAM_TEMPLATES = {
    "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
    "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
    "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"],
}

WORKOUT_TYPES = ("Strength", "Hypertrophy", "Conditioning", "Mixed", "Mobility")
MEMBERSHIP_STATUSES = ("Active", "Inactive")


class ValidationError(ValueError):
    """Raised when input data does not meet the rules."""


def get_program(code):
    """Return the program for a code such as 'fl' or 'FL'."""
    key = str(code).strip().upper()
    if key not in PROGRAMS:
        raise ValidationError(
            "program must be one of: " + ", ".join(sorted(PROGRAMS))
        )
    return key, PROGRAMS[key]


def calculate_calories(weight_kg, program_code):
    """Daily calories = weight (kg) x program calorie factor (whole number)."""
    _, program = get_program(program_code)
    return int(weight_kg * program["calorie_factor"])


def calculate_bmi(weight_kg, height_cm):
    """Return (bmi, category, risk_note). BMI is rounded to 1 decimal place."""
    if weight_kg <= 0 or height_cm <= 0:
        raise ValidationError("weight_kg and height_cm must be greater than 0")
    height_m = height_cm / 100.0
    bmi = round(weight_kg / (height_m * height_m), 1)
    if bmi < 18.5:
        return bmi, "Underweight", "Potential nutrient deficiency, low energy."
    if bmi < 25:
        return bmi, "Normal", "Low risk if active and strong."
    if bmi < 30:
        return (
            bmi,
            "Overweight",
            "Moderate risk; focus on adherence and progressive activity.",
        )
    return (
        bmi,
        "Obese",
        "Higher risk; prioritize fat loss, consistency, and supervision.",
    )


def parse_date(value, field="date"):
    """Turn 'YYYY-MM-DD' into a date object, or raise ValidationError."""
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise ValidationError(field + " must be in YYYY-MM-DD format")


def check_membership(status, end_date=None, today=None):
    """Return a membership summary.

    A membership is active only when its status is 'Active' and the end date
    (if there is one) has not passed.
    """
    today = today or date.today()
    expired = False
    if end_date:
        expired = parse_date(end_date, "membership_end") < today
    return {
        "status": status,
        "renewal_date": end_date if end_date else "N/A",
        "is_active": status == "Active" and not expired,
    }


def validate_adherence(value):
    """Weekly adherence is a whole number from 0 to 100 (percent)."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError("adherence must be a whole number")
    if not 0 <= value <= 100:
        raise ValidationError("adherence must be between 0 and 100")
    return value


def average_adherence(entries):
    """Average of the 'adherence' values, rounded to 1 decimal; 0.0 if empty."""
    if not entries:
        return 0.0
    return round(sum(e["adherence"] for e in entries) / len(entries), 1)


def generate_program(program_type=None, rng=None):
    """Pick a program type and a plan for it.

    Pass an rng (random.Random) to make the choice repeatable in tests.
    """
    rng = rng or random.Random()
    if program_type is None:
        program_type = rng.choice(sorted(PROGRAM_TEMPLATES))
    if program_type not in PROGRAM_TEMPLATES:
        raise ValidationError(
            "program_type must be one of: "
            + ", ".join(sorted(PROGRAM_TEMPLATES))
        )
    return program_type, rng.choice(PROGRAM_TEMPLATES[program_type])
