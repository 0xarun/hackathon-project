from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
import requests
from django.contrib.auth import login, logout
from .models import Habit, WellnessEntry, HealthTip
from .forms import HabitForm, WellnessEntryForm, UserRegistrationForm, UserLoginForm, ProfileForm
import random
from django.http import JsonResponse
from django.template.loader import render_to_string
from calendar import monthrange
import calendar

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('tracker:dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'tracker/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('tracker:dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'tracker/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('tracker:login')

@login_required
def dashboard(request):
    habits = Habit.objects.filter(user=request.user)
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    
    # Get entries for the current week
    week_entries = WellnessEntry.objects.filter(
        habit__in=habits,
        date__gte=week_start,
        date__lte=today
    ).select_related('habit')
    
    # Calculate weekly data
    week_data = {}
    weekly_scores = []
    
    for i in range(7):
        current_date = week_start + timedelta(days=i)
        day_entries = [e for e in week_entries if e.date == current_date]
        
        completed = sum(1 for e in day_entries if e.completed)
        total = len(habits)
        percentage = (completed / total * 100) if total > 0 else 0
        
        week_data[current_date] = {
            'completed': completed,
            'total': total,
            'percentage': percentage
        }
        
        if current_date <= today:
            weekly_scores.append(percentage)
    
    # Calculate weekly average
    weekly_average = sum(weekly_scores) / len(weekly_scores) if weekly_scores else 0
    
    # Calculate streak
    streak_days = 0
    current_date = today
    while True:
        day_data = week_data.get(current_date, {'completed': 0, 'total': len(habits)})
        if day_data['completed'] == day_data['total'] and day_data['total'] > 0:
            streak_days += 1
            current_date -= timedelta(days=1)
        else:
            break
    
    # Calculate completion rate
    total_entries = WellnessEntry.objects.filter(
        habit__in=habits,
        date__lte=today
    ).count()
    total_possible = len(habits) * (today - week_start).days
    completion_rate = (total_entries / total_possible * 100) if total_possible > 0 else 0
    
    # Calculate wellness score (0-100)
    wellness_score = 0
    if habits:
        # Base score from completion rate
        wellness_score += completion_rate * 0.4  # 40% weight
        
        # Streak bonus
        streak_bonus = min(streak_days * 5, 30)  # Up to 30% bonus for streaks
        wellness_score += streak_bonus
        
        # Weekly average bonus
        weekly_bonus = min(weekly_average * 0.3, 30)  # Up to 30% bonus for weekly average
        wellness_score += weekly_bonus
    
    # Get today's entries
    today_entries = {e.habit_id: e for e in week_entries if e.date == today}
    
    # Add completion status and today's value to habits
    for habit in habits:
        habit.completed = habit.id in today_entries and today_entries[habit.id].completed
        habit.today_value = today_entries[habit.id].value if habit.id in today_entries else None
    
    # Calculate today's score
    today_score = sum(1 for habit in habits if habit.completed)
    
    # Get health tips
    health_tips = [
        "Stay hydrated! Drink at least 8 glasses of water daily.",
        "Get 7-9 hours of sleep for optimal health.",
        "Take regular breaks from screen time.",
        "Practice mindfulness for 5-10 minutes daily.",
        "Include protein in every meal.",
        "Take a 10-minute walk after meals.",
        "Stretch for 5 minutes every hour.",
        "Practice deep breathing exercises.",
        "Eat a rainbow of fruits and vegetables.",
        "Limit processed foods and added sugars."
    ]
    health_tip = random.choice(health_tips)

    context = {
        'habits': habits,
        'today_score': today_score,
        'weekly_average': weekly_average,
        'streak_days': streak_days,
        'completion_rate': completion_rate,
        'week_data': week_data,
        'today': today,
        'health_tip': health_tip,
        'wellness_score': min(round(wellness_score), 100),  # Cap at 100
    }
    return render(request, 'tracker/dashboard.html', context)

def habit_create(request):
    if request.method == 'POST':
        form = HabitForm(request.POST)
        if form.is_valid():
            habit = form.save(commit=False)
            habit.user = request.user
            habit.save()
            messages.success(request, 'Habit created successfully!')
            return redirect('tracker:dashboard')
    else:
        form = HabitForm()
    return render(request, 'tracker/habit_form.html', {'form': form})


def log_entry(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    today = timezone.now().date()
    
    if request.method == 'POST':
        form = WellnessEntryForm(request.POST, habit=habit, date=today)
        if form.is_valid():
            # Try to get existing entry or create new one
            entry, created = WellnessEntry.objects.get_or_create(
                habit=habit,
                date=today,
                defaults={'value': form.cleaned_data['value']}
            )
            if not created:
                # Update existing entry
                entry.value = form.cleaned_data['value']
                entry.save()
            messages.success(request, 'Entry logged successfully!')
            return redirect('tracker:dashboard')
    else:
        form = WellnessEntryForm(habit=habit, date=today)
    
    return render(request, 'tracker/log_entry.html', {'form': form, 'habit': habit})

@login_required
def calendar_view(request):
    habits = Habit.objects.filter(user=request.user)
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    start_date = today.replace(year=year, month=month, day=1)
    last_day = monthrange(year, month)[1]
    end_date = start_date.replace(day=last_day)

    entries = WellnessEntry.objects.filter(
        habit__in=habits,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('habit')

    # Group entries by date
    calendar_data = {}
    for entry in entries:
        if entry.date not in calendar_data:
            calendar_data[entry.date] = []
        calendar_data[entry.date].append(entry)

    # For each day, build a summary of completed/missed habits
    days = []
    for day in range(1, last_day + 1):
        date = start_date.replace(day=day)
        day_entries = calendar_data.get(date, [])
        completed = [e for e in day_entries if e.completed]
        missed = [e for e in day_entries if not e.completed]
        days.append({
            'date': date,
            'completed': completed,
            'missed': missed,
            'all': day_entries,
        })

    # Group days into weeks for calendar grid
    weeks = []
    week = []
    # Find the weekday of the first day (0=Monday, 6=Sunday)
    first_weekday = days[0]['date'].weekday()
    # Pad the first week with None if the month doesn't start on Sunday
    pad = (days[0]['date'].weekday() + 1) % 7  # 0=Sunday, 6=Saturday
    for _ in range(pad):
        week.append(None)
    for day in days:
        week.append(day)
        if len(week) == 7:
            weeks.append(week)
            week = []
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)

    return render(request, 'tracker/calendar.html', {
        'weeks': weeks,
        'habits': habits,
        'year': year,
        'month': month,
        'today': today,
    })

@login_required
def day_progress(request, year, month, day):
    habits = Habit.objects.filter(user=request.user)
    date = timezone.datetime(year, month, day).date()
    entries = WellnessEntry.objects.filter(habit__in=habits, date=date).select_related('habit')
    return render(request, 'tracker/day_progress_panel.html', {
        'date': date,
        'entries': entries,
        'habits': habits,
    })

@login_required
def weekly_report(request):
    today = timezone.now().date()
    start_date = today - timedelta(days=6)  # Last 7 days including today
    
    habits = Habit.objects.filter(user=request.user)
    entries = WellnessEntry.objects.filter(
        habit__in=habits,
        date__gte=start_date,
        date__lte=today
    ).select_related('habit')
    
    # Calculate daily completion data
    daily_data = {}
    for i in range(7):
        current_date = start_date + timedelta(days=i)
        day_entries = [e for e in entries if e.date == current_date]
        completed = sum(1 for e in day_entries if e.value >= e.habit.target_value)
        daily_data[current_date] = completed
    
    # Calculate weekly statistics
    weekly_stats = {
        'completion_rate': 0,
        'average_score': 0,
        'total_entries': len(entries),
        'completed_entries': sum(1 for e in entries if e.value >= e.habit.target_value)
    }
    
    if weekly_stats['total_entries'] > 0:
        weekly_stats['completion_rate'] = (weekly_stats['completed_entries'] / weekly_stats['total_entries']) * 100
        weekly_stats['average_score'] = weekly_stats['completed_entries'] / len(habits)
    
    # Add weekly completion method to Habit model
    for habit in habits:
        habit_entries = [e for e in entries if e.habit == habit]
        completed = sum(1 for e in habit_entries if e.value >= habit.target_value)
        habit.get_weekly_completion = lambda: (completed / len(habit_entries) * 100) if habit_entries else 0
    
    context = {
        'weekly_stats': weekly_stats,
        'habits': habits,
        'daily_data': daily_data,
        'start_date': start_date,
        'end_date': today
    }
    
    return render(request, 'tracker/weekly_report.html', context)

@login_required
def habit_delete(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    if request.method == 'POST':
        habit.delete()
        messages.success(request, 'Habit deleted successfully!')
        return redirect('tracker:dashboard')
    return render(request, 'tracker/habit_confirm_delete.html', {'habit': habit})

@login_required
def habit_progress_panel(request, habit_id):
    habit = get_object_or_404(Habit, id=habit_id, user=request.user)
    entries = WellnessEntry.objects.filter(habit=habit).order_by('date')
    if entries.exists():
        dates = [e.date.strftime('%Y-%m-%d') for e in entries]
        values = [e.value for e in entries]
        completed_days = sum(1 for e in entries if e.value >= habit.target_value)
        streak = 0
        max_streak = 0
        last_date = None
        for e in entries:
            if e.value >= habit.target_value:
                if last_date and (e.date - last_date).days == 1:
                    streak += 1
                else:
                    streak = 1
                max_streak = max(max_streak, streak)
                last_date = e.date
        context = {
            'habit': habit,
            'entries': entries,
            'dates': dates,
            'values': values,
            'completed_days': completed_days,
            'max_streak': max_streak,
        }
        html = render_to_string('tracker/habit_progress_panel.html', context, request=request)
        return JsonResponse({'html': html})
    else:
        html = render_to_string('tracker/habit_progress_panel.html', {'habit': habit, 'no_progress': True}, request=request)
        return JsonResponse({'html': html})

@login_required
def profile_settings(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('tracker:profile_settings')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'tracker/profile_settings.html', {'form': form, 'profile': profile})

@login_required
def all_habits(request):
    habits = Habit.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tracker/all_habits.html', {'habits': habits})
