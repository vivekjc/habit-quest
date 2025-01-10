from flask import current_app as app
from flask import render_template, request, jsonify, redirect, url_for
from app.models import db, Habit, HabitCompletion, Player, Achievement
from datetime import datetime, timedelta
import json

@app.route('/')
def index():
    habits = Habit.query.all()
    return render_template('dashboard.html', habits=habits)

@app.route('/calendar')
def calendar():
    habits = Habit.query.all()
    habit_data = []
    total_completions = 0
    perfect_days = 0
    best_streak = 0
    
    for habit in habits:
        completions = HabitCompletion.query.filter_by(habit_id=habit.id).order_by(HabitCompletion.completed_at).all()
        completion_dates = [c.completed_at.date() for c in completions]
        
        # Calculate yearly data for heatmap
        yearly_data = []
        today = datetime.utcnow().date()
        for i in range(52):
            week_start = today - timedelta(days=today.weekday(), weeks=i)
            week_completions = len([d for d in completion_dates if week_start <= d <= week_start + timedelta(days=6)])
            
            # Calculate color based on completions
            intensity = min(1.0, week_completions / (7 if habit.frequency == 'daily' else 1))
            color = f"rgba(34, 197, 94, {intensity})"  # green with varying opacity
            
            yearly_data.append({
                'color': color,
                'tooltip': f"{week_completions} completions in week of {week_start.strftime('%Y-%m-%d')}"
            })
        
        # Calculate weekly pattern
        weekly_pattern = [0] * 7
        for date in completion_dates:
            weekly_pattern[date.weekday()] += 1
        
        # Calculate monthly averages for trend data
        months = {}
        for completion in completions:
            month_key = completion.completed_at.strftime('%Y-%m')
            months[month_key] = months.get(month_key, 0) + 1
        
        trend_data = [months.get(month, 0) for month in sorted(months.keys())]
        
        habit_data.append({
            'id': habit.id,
            'name': habit.name,
            'frequency': habit.frequency,
            'streak': habit.get_streak(),
            'best_streak': calculate_best_streak(completions),
            'total_completions': len(completions),
            'monthly_average': round(len(completions) / max(1, len(months)), 1),
            'completion_rate': round(len(completion_dates) / 365 * 100, 1),
            'yearly_data': yearly_data,
            'weekly_pattern': weekly_pattern,
            'trend_data': trend_data,
            'color': f"hsl({hash(habit.name) % 360}, 70%, 50%)"
        })
        
        total_completions += len(completions)
        best_streak = max(best_streak, calculate_best_streak(completions))
    
    # Calculate perfect days (all habits completed)
    all_completion_dates = [c.completed_at.date() for c in HabitCompletion.query.all()]
    date_counts = {}
    for date in all_completion_dates:
        date_counts[date] = date_counts.get(date, 0) + 1
    perfect_days = sum(1 for count in date_counts.values() if count >= len(habits))
    
    # Calculate overall consistency for last 30 days
    today = datetime.utcnow().date()
    last_30_days = set(today - timedelta(days=x) for x in range(30))
    completed_days = set(d for d in all_completion_dates if d in last_30_days)
    consistency = round(len(completed_days) / 30 * 100, 1)
    
    # Generate labels for trends chart (last 12 months)
    trends_labels = []
    for i in range(11, -1, -1):
        month = datetime.utcnow() - timedelta(days=i*30)
        trends_labels.append(month.strftime('%b %Y'))

    return render_template('calendar.html',
                         habits=habit_data,
                         habits_json=json.dumps(habit_data),
                         trends_labels=json.dumps(trends_labels),
                         total_completions=total_completions,
                         perfect_days=perfect_days,
                         best_streak=best_streak,
                         consistency=consistency)

def calculate_best_streak(completions):
    if not completions:
        return 0
    
    # Sort completions by date
    dates = sorted(set(c.completed_at.date() for c in completions))
    if not dates:
        return 0
        
    best_streak = current_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i-1]).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 1
            
    return best_streak

def calculate_month_completions(completions):
    today = datetime.utcnow()
    return len([c for c in completions 
               if c.completed_at.year == today.year 
               and c.completed_at.month == today.month])

@app.route('/add_habit', methods=['POST'])
def add_habit():
    data = request.json
    new_habit = Habit(
        name=data['name'],
        frequency=data['frequency'],
        times_per_day=data.get('times_per_day', 1)
    )
    db.session.add(new_habit)
    db.session.commit()
    return jsonify({'success': True, 'id': new_habit.id})

@app.route('/complete_habit/<int:habit_id>', methods=['POST'])
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    player = Player.query.first()  # Or get from session
    
    if not habit.is_completed_today():
        completion = HabitCompletion(habit_id=habit_id)
        db.session.add(completion)
        
        # Award XP and check level up
        xp_gained = 10
        player.xp += xp_gained
        
        # Check for level up
        next_level_xp = player.level * 100
        if player.xp >= next_level_xp:
            player.level += 1
            level_up = True
        else:
            level_up = False
            
        # Check for achievements
        new_achievements = Achievement.check_achievements(player, habit)
        for achievement in new_achievements:
            db.session.add(Achievement(**achievement, player_id=player.id))
            
        db.session.commit()
        
        return jsonify({
            'success': True,
            'xp_gained': xp_gained,
            'level_up': level_up,
            'new_level': player.level if level_up else None,
            'new_achievements': new_achievements,
            'streak': habit.get_streak()
        })
    
    return jsonify({
        'success': False,
        'message': 'Already completed maximum times for today'
    })

@app.route('/uncomplete_habit/<int:habit_id>', methods=['POST'])
def uncomplete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    completion = habit.get_today_completion()
    if completion:
        db.session.delete(completion)
        db.session.commit()
    return jsonify({
        'success': True,
        'streak': habit.get_streak(),
        'completed': False
    })

@app.route('/get_completions/<int:habit_id>')
def get_completions(habit_id):
    completions = HabitCompletion.query.filter_by(habit_id=habit_id).all()
    return jsonify([c.completed_at.strftime('%Y-%m-%d') for c in completions])

@app.route('/debug')
def debug():
    habits = Habit.query.all()
    habit_data = []
    for habit in habits:
        completions = HabitCompletion.query.filter_by(habit_id=habit.id).order_by(HabitCompletion.completed_at.desc()).all()
        habit_data.append({
            'id': habit.id,
            'name': habit.name,
            'frequency': habit.frequency,
            'times_per_day': habit.times_per_day,
            'created_at': habit.created_at,
            'streak': habit.get_streak(),
            'completions': [
                {
                    'id': c.id,
                    'completed_at': c.completed_at
                } for c in completions
            ]
        })
    return render_template('debug.html', habits=habit_data)

@app.route('/reset_data', methods=['POST'])
def reset_data():
    try:
        # Delete all completions first (due to foreign key constraint)
        HabitCompletion.query.delete()
        # Delete all habits
        Habit.query.delete()
        db.session.commit()
        return jsonify({'success': True, 'message': 'All data has been reset'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500 

@app.route('/habit_history/<int:habit_id>')
def habit_history(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    completions = HabitCompletion.query.filter_by(habit_id=habit_id)\
        .order_by(HabitCompletion.completed_at.desc())\
        .all()
    
    history = [{
        'date': c.completed_at.strftime('%Y-%m-%d'),
        'time': c.completed_at.strftime('%I:%M %p'),
        'completions': 1
    } for c in completions]
    
    # Group completions by date
    from itertools import groupby
    from operator import itemgetter
    
    grouped_history = []
    for date, items in groupby(history, key=itemgetter('date')):
        completions = list(items)
        grouped_history.append({
            'date': date,
            'time': completions[0]['time'],
            'completions': len(completions)
        })
    
    return jsonify({
        'success': True,
        'history': grouped_history
    }) 

@app.route('/edit_habit/<int:habit_id>', methods=['POST'])
def edit_habit(habit_id):
    try:
        habit = Habit.query.get_or_404(habit_id)
        data = request.json
        
        habit.name = data.get('name', habit.name)
        habit.frequency = data.get('frequency', habit.frequency)
        habit.times_per_day = data.get('times_per_day', habit.times_per_day)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'habit': {
                'id': habit.id,
                'name': habit.name,
                'frequency': habit.frequency,
                'times_per_day': habit.times_per_day,
                'streak': habit.get_streak()
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400 

@app.route('/analyze_habits')
def analyze_habits():
    habits = Habit.query.all()
    analysis_data = {}
    
    # Get all completion dates for correlation analysis
    habit_completions = {}
    for habit in habits:
        dates = set(c.completed_at.date() for c in habit.completions)
        habit_completions[habit.id] = dates

    # Calculate correlations
    correlations = []
    for h1 in habits:
        for h2 in habits:
            if h1.id < h2.id:  # Avoid duplicate combinations
                dates1 = habit_completions[h1.id]
                dates2 = habit_completions[h2.id]
                
                # Calculate correlation coefficient
                both_completed = len(dates1.intersection(dates2))
                either_completed = len(dates1.union(dates2))
                if either_completed > 0:
                    correlation = both_completed / either_completed
                    if correlation > 0.3:  # Only show significant correlations
                        correlations.append({
                            'habit1': h1.name,
                            'habit2': h2.name,
                            'strength': round(correlation * 100, 1)
                        })

    # Calculate projections
    projections = []
    for habit in habits:
        completions = list(habit_completions[habit.id])
        if len(completions) >= 14:  # Need at least 2 weeks of data
            # Calculate trend
            recent_rate = len([d for d in completions if d >= datetime.utcnow().date() - timedelta(days=14)]) / 14
            overall_rate = len(completions) / (max(completions).toordinal() - min(completions).toordinal() + 1)
            
            trend = 'improving' if recent_rate > overall_rate else 'declining'
            projected_days_to_goal = None
            
            if habit.frequency == 'daily':
                if recent_rate < 1:
                    days_to_habit = round((1 - recent_rate) / (recent_rate - overall_rate) * 14)
                    if days_to_habit > 0:
                        projected_days_to_goal = days_to_habit

            projections.append({
                'habit_name': habit.name,
                'current_rate': round(recent_rate * 100, 1),
                'trend': trend,
                'days_to_goal': projected_days_to_goal
            })

    # Export data preparation
    export_data = {
        'habits': [{
            'name': habit.name,
            'frequency': habit.frequency,
            'completions': sorted(str(date) for date in habit_completions[habit.id])
        } for habit in habits]
    }

    return jsonify({
        'correlations': correlations,
        'projections': projections,
        'export_data': export_data
    }) 