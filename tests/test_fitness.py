"""Unit tests for the pure business logic in fitness.py."""
import random
from datetime import date

import pytest

import fitness
from fitness import ValidationError


# ---------- programs and calories ----------
@pytest.mark.parametrize("code, weight, expected", [
    ("FL", 70, 1540),    # 70 x 22
    ("MG", 70, 2450),    # 70 x 35
    ("BG", 70, 1820),    # 70 x 26
    ("fl", 70, 1540),    # code is not case sensitive
    ("FL", 65.5, 1441),  # 65.5 x 22 = 1441.0
    ("MG", 60.7, 2124),  # 2124.5 is cut down to a whole number
])
def test_calculate_calories(code, weight, expected):
    assert fitness.calculate_calories(weight, code) == expected


def test_unknown_program_is_rejected():
    with pytest.raises(ValidationError):
        fitness.calculate_calories(70, "XX")


def test_get_program_returns_code_and_details():
    code, program = fitness.get_program(" mg ")
    assert code == "MG"
    assert program["name"] == "Muscle Gain"
    assert program["calorie_factor"] == 35


# ---------- BMI ----------
@pytest.mark.parametrize("weight, height, bmi, category", [
    (50, 175, 16.3, "Underweight"),
    (70, 175, 22.9, "Normal"),
    (85, 175, 27.8, "Overweight"),
    (110, 175, 35.9, "Obese"),
])
def test_calculate_bmi_categories(weight, height, bmi, category):
    result = fitness.calculate_bmi(weight, height)
    assert result[0] == bmi
    assert result[1] == category
    assert result[2]  # every category has a risk note


@pytest.mark.parametrize("weight, height, category", [
    (56.7, 175, "Normal"),      # BMI 18.5 is the first Normal value
    (76.5, 175, "Overweight"),  # BMI 25.0 is the first Overweight value
    (91.9, 175, "Obese"),       # BMI 30.0 is the first Obese value
])
def test_bmi_boundaries(weight, height, category):
    assert fitness.calculate_bmi(weight, height)[1] == category


@pytest.mark.parametrize("weight, height", [(0, 175), (70, 0), (-5, 170)])
def test_bmi_rejects_non_positive_values(weight, height):
    with pytest.raises(ValidationError):
        fitness.calculate_bmi(weight, height)


# ---------- membership ----------
TODAY = date(2026, 10, 4)


def test_membership_active_without_end_date():
    result = fitness.check_membership("Active", None, TODAY)
    assert result == {"status": "Active", "renewal_date": "N/A",
                      "is_active": True}


def test_membership_active_until_end_date_inclusive():
    assert fitness.check_membership("Active", "2026-10-04", TODAY)["is_active"]
    assert fitness.check_membership("Active", "2027-01-01", TODAY)["is_active"]


def test_membership_expired_when_end_date_passed():
    result = fitness.check_membership("Active", "2026-10-03", TODAY)
    assert result["is_active"] is False


def test_membership_inactive_status_is_never_active():
    assert fitness.check_membership("Inactive", None, TODAY)["is_active"] is False


def test_membership_bad_date_is_rejected():
    with pytest.raises(ValidationError):
        fitness.check_membership("Active", "04-10-2026", TODAY)


# ---------- adherence ----------
@pytest.mark.parametrize("value", [0, 50, 100])
def test_validate_adherence_accepts_valid(value):
    assert fitness.validate_adherence(value) == value


@pytest.mark.parametrize("value", [-1, 101, 55.5, "80", None, True])
def test_validate_adherence_rejects_invalid(value):
    with pytest.raises(ValidationError):
        fitness.validate_adherence(value)


def test_average_adherence():
    entries = [{"adherence": 80}, {"adherence": 90}, {"adherence": 75}]
    assert fitness.average_adherence(entries) == 81.7
    assert fitness.average_adherence([]) == 0.0


# ---------- program generator ----------
def test_generate_program_is_repeatable_with_a_seed():
    first = fitness.generate_program(rng=random.Random(7))
    second = fitness.generate_program(rng=random.Random(7))
    assert first == second


def test_generate_program_for_a_chosen_type():
    program_type, plan = fitness.generate_program("Beginner",
                                                  rng=random.Random(1))
    assert program_type == "Beginner"
    assert plan in fitness.PROGRAM_TEMPLATES["Beginner"]


def test_generate_program_random_type_comes_from_templates():
    program_type, plan = fitness.generate_program(rng=random.Random(3))
    assert plan in fitness.PROGRAM_TEMPLATES[program_type]


def test_generate_program_rejects_unknown_type():
    with pytest.raises(ValidationError):
        fitness.generate_program("Yoga")
