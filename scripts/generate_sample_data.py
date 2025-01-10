from datetime import datetime, timedelta
import random
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db, Habit, HabitCompletion

def generate_sample_data():
    app = create_app()
    
    with app.app_context():
        # Clear existing data
        HabitCompletion.query.delete()
        Habit.query.delete()
        db.session.commit()
        
        # Create sample habits
        habits = [
            {
                'name': 'Morning Meditation',
                'frequency': 'daily',
                'times_per_day': 1,
                'consistency': 0.9  # 90% consistent
            },
            {
                'name': 'Exercise',
                'frequency': 'daily',
                'times_per_day': 1,
                'consistency': 0.7  # 70% consistent
            },
            {
                'name': 'Read Books',
                'frequency': 'daily',
                'times_per_day': 2,
                'consistency': 0.8  # 80% consistent
            },
            {
                'name': 'Practice Guitar',
                'frequency': 'weekly',
                'times_per_day': 1,
                'consistency': 0.6  # 60% consistent
            },
            {
                'name': 'Drink Water',
                'frequency': 'daily',
                'times_per_day': 8,
                'consistency': 0.85  # 85% consistent
            }
        ]
        
        # Create habits
        habit_objects = []
        for habit_data in habits:
            habit = Habit(
                name=habit_data['name'],
                frequency=habit_data['frequency'],
                times_per_day=habit_data['times_per_day']
            )
            db.session.add(habit)
            habit_objects.append((habit, habit_data['consistency']))
        
        db.session.commit()
        
        # Generate completions for the past year
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)
        current_date = start_date
        
        while current_date <= end_date:
            for habit, consistency in habit_objects:
                # Determine if habit should be completed based on consistency
                if random.random() < consistency:
                    # For habits with multiple completions per day
                    completions_today = random.randint(
                        max(1, int(habit.times_per_day * 0.7)),  # At least 70% of daily goal
                        habit.times_per_day
                    )
                    
                    # Skip some days for weekly habits
                    if habit.frequency == 'weekly' and current_date.weekday() != 0:  # Monday
                        continue
                    
                    # Create completions
                    for _ in range(completions_today):
                        # Random time between 6 AM and 10 PM
                        hour = random.randint(6, 22)
                        minute = random.randint(0, 59)
                        completion_time = current_date.replace(hour=hour, minute=minute)
                        
                        completion = HabitCompletion(
                            habit_id=habit.id,
                            completed_at=completion_time
                        )
                        db.session.add(completion)
            
            current_date += timedelta(days=1)
        
        db.session.commit()
        
        # Print summary
        print("\nSample data generated successfully!")
        print("\nHabits created:")
        for habit, _ in habit_objects:
            completions = HabitCompletion.query.filter_by(habit_id=habit.id).count()
            print(f"\n{habit.name}:")
            print(f"- Total completions: {completions}")
            print(f"- Current streak: {habit.get_streak()} days")
            print(f"- Times per day: {habit.times_per_day}")

if __name__ == "__main__":
    generate_sample_data() 