from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, custom
    times_per_day = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completions = db.relationship('HabitCompletion', backref='habit', lazy=True)

    @property
    def status(self):
        """Return the current status of the habit (for character display)"""
        completions_today = self.get_completions_today()
        if completions_today >= self.times_per_day:
            return 'celebrating'
        elif completions_today > 0:
            return 'happy'
        elif self.get_streak() > 0:
            return 'happy'
        return 'sleeping'

    @property
    def progress(self):
        """Return the progress percentage for today"""
        return min(100, (self.get_completions_today() * 100) // self.times_per_day)

    @property
    def streak(self):
        """Return the current streak (alias for get_streak)"""
        return self.get_streak()

    @property
    def badges(self):
        """Return earned badges"""
        badges = []
        streak = self.get_streak()
        total_completions = len(self.completions)

        if streak >= 7:
            badges.append({
                'emoji': '🔥',
                'description': f'{streak} day streak!'
            })
        if total_completions >= 100:
            badges.append({
                'emoji': '💯',
                'description': '100 completions!'
            })
        if self.get_perfect_week_count() > 0:
            badges.append({
                'emoji': '⭐',
                'description': f'{self.get_perfect_week_count()} perfect weeks!'
            })
        return badges

    def get_perfect_week_count(self):
        """Count the number of weeks where all days were completed"""
        if self.frequency != 'daily':
            return 0

        completions_by_date = {}
        for completion in self.completions:
            date = completion.completed_at.date()
            completions_by_date[date] = completions_by_date.get(date, 0) + 1

        perfect_weeks = 0
        current_date = datetime.utcnow().date()
        for i in range(52):  # Check last 52 weeks
            week_start = current_date - timedelta(days=current_date.weekday() + 7 * i)
            week_perfect = True
            for day in range(7):
                date = week_start + timedelta(days=day)
                if completions_by_date.get(date, 0) < self.times_per_day:
                    week_perfect = False
                    break
            if week_perfect:
                perfect_weeks += 1

        return perfect_weeks

    def get_streak(self):
        """Calculate the current streak"""
        completions = HabitCompletion.query.filter_by(habit_id=self.id).order_by(HabitCompletion.completed_at.desc()).all()
        if not completions:
            return 0
            
        streak = 0
        today = datetime.utcnow().date()
        expected_date = today
        
        # Group completions by date
        completion_dates = {}
        for completion in completions:
            date = completion.completed_at.date()
            completion_dates[date] = completion_dates.get(date, 0) + 1

        # Check streak
        while expected_date in completion_dates:
            if completion_dates[expected_date] >= self.times_per_day:
                streak += 1
                expected_date -= timedelta(days=1)
            else:
                break

        return streak

    def get_completions_today(self):
        """Count completions for today"""
        today = datetime.utcnow().date()
        return HabitCompletion.query.filter(
            HabitCompletion.habit_id == self.id,
            db.func.date(HabitCompletion.completed_at) == today
        ).count()

    def is_completed_today(self):
        """Check if habit is completed for today"""
        return self.get_completions_today() >= self.times_per_day

    @property
    def completions_today(self):
        """Return number of completions today (for template)"""
        return self.get_completions_today()

    @property
    def is_completed(self):
        """Check if habit is completed (for template)"""
        return self.is_completed_today()

class HabitCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow) 

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    streak_points = db.Column(db.Integer, default=0)
    achievements = db.relationship('Achievement', backref='player', lazy=True)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    emoji = db.Column(db.String(10))
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'))
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def check_achievements(player, habit):
        achievements = []
        
        # Check streak achievements
        if habit.get_streak() >= 7:
            achievements.append({
                'name': 'Week Warrior',
                'description': 'Maintained a 7-day streak!',
                'emoji': '🔥'
            })
        
        # Check completion achievements
        total_completions = len(habit.completions)
        if total_completions >= 100:
            achievements.append({
                'name': 'Century Club',
                'description': 'Completed a habit 100 times!',
                'emoji': '💯'
            })
        
        return achievements 