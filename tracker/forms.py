from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Habit, WellnessEntry, Profile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Use email as username
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')  # Change username label to Email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'habit_type', 'target_value']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter habit name'}),
            'habit_type': forms.Select(attrs={'class': 'form-control'}),
            'target_value': forms.NumberInput(attrs={'class': 'form-control', 'min': '0.1', 'step': '0.1'}),
        }

class WellnessEntryForm(forms.ModelForm):
    class Meta:
        model = WellnessEntry
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        self.habit = kwargs.pop('habit', None)
        self.date = kwargs.pop('date', None)
        super().__init__(*args, **kwargs)
        if self.habit:
            self.fields['value'].widget.attrs['placeholder'] = f'Enter {self.habit.unit}'
            self.fields['value'].label = f'How many {self.habit.unit}?'

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'profile_image']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        } 