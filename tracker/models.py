from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Habit(models.Model):
    """A habit tracked by the user."""
    HABIT_TYPES = [
        ('exercise', 'Exercise'),
        ('sleep', 'Sleep'),
        ('water', 'Water Intake'),
        ('meditation', 'Meditation'),
        ('skincare', 'Skincare'),
        ('reading', 'Reading'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    habit_type = models.CharField(max_length=20, choices=HABIT_TYPES)
    target_value = models.FloatField(default=1)
    unit = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_habit_type_display()})"
    
    def get_default_unit(self):
        units = {
            'exercise': 'minutes',
            'sleep': 'hours',
            'water': 'glasses',
            'meditation': 'minutes',
            'skincare': 'times',
            'reading': 'minutes',
            'other': 'times',
        }
        return units.get(self.habit_type, 'times')
    
    def save(self, *args, **kwargs):
        if not self.unit:
            self.unit = self.get_default_unit()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', 'created_at'])]

class WellnessEntry(models.Model):
    """A daily log entry for a habit."""
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    value = models.FloatField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('habit', 'date')
        ordering = ['-date']
        indexes = [models.Index(fields=['habit', 'date'])]
    
    def save(self, *args, **kwargs):
        self.completed = self.value >= self.habit.target_value
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.habit.name} - {self.date}: {self.value} {self.habit.unit}"

class HealthTip(models.Model):
    """A health tip for users."""
    tip = models.TextField()
    source = models.CharField(max_length=100)
    category = models.CharField(max_length=50, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tip from {self.source}"

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['category', 'created_at'])]

class Profile(models.Model):
    """User profile with extra info."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')

    def __str__(self):
        return self.full_name or self.user.email or str(self.user)

    def get_profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return 'https://randomuser.me/api/portraits/lego/1.jpg'

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        if not hasattr(instance, 'profile'):
            Profile.objects.create(user=instance)
        else:
            instance.profile.save()
