# generate_dataset.py
# Synopsis challenge: "Finding or building a reliable career-skill mapping dataset,
# since ready-made datasets are limited." -> Solution: generate a synthetic dataset
# by simulating many student profiles for each career, based on real-world required
# skills, with some random noise (extra unrelated skills / missing a couple of skills)
# so the model learns a realistic, non-perfect pattern instead of memorizing.

import random
import csv
import os
import sys

sys.path.append(os.path.dirname(__file__))
from career_skill_map import CAREER_SKILL_MAP, ALL_SKILLS

random.seed(42)

OUT_PATH = os.path.join(os.path.dirname(__file__), "career_dataset.csv")
SAMPLES_PER_CAREER = 120


def generate_profile(career_skills):
    """Simulate one student's skill profile for a given career."""
    profile = set(career_skills)

    # Randomly drop 0-2 of the "required" skills (nobody has 100% of skills)
    drop_count = random.choice([0, 0, 1, 1, 2])
    if drop_count and len(profile) > 2:
        for s in random.sample(list(profile), min(drop_count, len(profile) - 2)):
            profile.discard(s)

    # Randomly add 0-3 unrelated skills (real students have mixed skill sets)
    other_skills = [s for s in ALL_SKILLS if s not in profile]
    add_count = random.choice([0, 1, 1, 2, 3])
    if other_skills and add_count:
        profile.update(random.sample(other_skills, min(add_count, len(other_skills))))

    return profile


def main():
    rows = []
    for career, info in CAREER_SKILL_MAP.items():
        for _ in range(SAMPLES_PER_CAREER):
            profile = generate_profile(info["skills"])
            row = {skill: (1 if skill in profile else 0) for skill in ALL_SKILLS}
            row["career"] = career
            rows.append(row)

    random.shuffle(rows)

    with open(OUT_PATH, "w", newline="") as f:
        fieldnames = ALL_SKILLS + ["career"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} training samples -> {OUT_PATH}")


if __name__ == "__main__":
    main()
