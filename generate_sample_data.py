#!/usr/bin/env python3
"""
Generate 2 years of sample Hevy workout data for testing purposes.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Sample exercises by muscle group
EXERCISES_BY_MUSCLE = {
    "Back": [
        "Bent Over Row (Barbell)",
        "Lat Pulldown (Cable)",
        "Seated Cable Row - Bar Grip",
        "Pull-ups (Assisted)",
    ],
    "Chest": [
        "Bench Press (Barbell)",
        "Incline Bench Press (Dumbbell)",
        "Cable Fly",
        "Push-ups",
    ],
    "Shoulders": [
        "Shoulder Press (Dumbbell)",
        "Lateral Raise (Dumbbell)",
        "Reverse Fly (Pec Deck)",
        "Shrug (Barbell)",
    ],
    "Arms": [
        "Barbell Curl",
        "Tricep Rope Pushdown (Cable)",
        "Preacher Curl (EZ-Bar)",
        "Overhead Extension (Dumbbell)",
    ],
    "Legs": [
        "Squat (Barbell)",
        "Leg Press (Plate Loaded)",
        "Leg Curl (Machine)",
        "Leg Extension (Machine)",
    ],
    "Core": [
        "Crunch (Machine)",
        "Cable Crunch",
        "Ab Wheel Rollout (Weighted)",
        "Plank (Bodyweight)",
    ],
}

def generate_sample_data(days=730):  # ~2 years
    """Generate sample Hevy workout data."""
    rows = []
    start_date = datetime.now() - timedelta(days=days)
    
    # Workout schedule: 4-5 times per week
    current_date = start_date
    workout_count = 0
    
    while current_date < datetime.now():
        # 80% chance of having a workout on any given day
        if random.random() < 0.8 and (current_date.weekday() < 5 or random.random() < 0.5):
            # Pick a random muscle group
            muscle_group = random.choice(list(EXERCISES_BY_MUSCLE.keys()))
            exercises = EXERCISES_BY_MUSCLE[muscle_group]
            
            # Generate workout details
            start_time = current_date.replace(hour=random.randint(6, 18), minute=random.randint(0, 59))
            duration_min = random.randint(45, 120)
            end_time = start_time + timedelta(minutes=duration_min)
            
            workout_title = f"{muscle_group} Day"
            
            # Generate 3-5 exercises per workout
            num_exercises = random.randint(3, 5)
            selected_exercises = random.sample(exercises, min(num_exercises, len(exercises)))
            
            for exercise_idx, exercise in enumerate(selected_exercises):
                # Generate 2-4 sets per exercise
                num_sets = random.randint(2, 4)
                
                for set_idx in range(num_sets):
                    # Weight and reps
                    weight_kg = random.randint(20, 120)
                    reps = random.randint(5, 15)
                    
                    # Set type: mostly normal, some warmup, some other
                    if set_idx == 0 and exercise_idx == 0:
                        set_type = "warmup"
                    elif random.random() < 0.1:
                        set_type = random.choice(["dropset", "myo", "failure"])
                    else:
                        set_type = "normal"
                    
                    rows.append({
                        "title": workout_title,
                        "start_time": start_time.strftime("%d %b %Y, %H:%M"),
                        "end_time": end_time.strftime("%d %b %Y, %H:%M"),
                        "description": "",
                        "exercise_title": exercise,
                        "superset_id": "",
                        "exercise_notes": "",
                        "set_index": set_idx,
                        "set_type": set_type,
                        "weight_kg": weight_kg,
                        "reps": reps,
                        "distance_km": "",
                        "duration_seconds": "",
                        "rpe": "",
                    })
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(rows)

if __name__ == "__main__":
    print("Generating 2 years of sample Hevy workout data...")
    df = generate_sample_data()
    
    output_path = "hevy_workouts_sample.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} records")
    print(f"Date range: {df['start_time'].min()} to {df['start_time'].max()}")
    print(f"Saved to {output_path}")
