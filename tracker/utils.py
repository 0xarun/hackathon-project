import requests
from django.conf import settings
from .models import HealthTip

def fetch_health_tip():
    """Fetch a health tip from API Ninjas and save it to the database."""
    try:
        response = requests.get(
            'https://api.api-ninjas.com/v1/quotes?category=health',
            headers={'X-Api-Key': settings.API_NINJAS_KEY}
        )
        response.raise_for_status()
        data = response.json()[0]
        
        # Create new health tip
        tip = HealthTip.objects.create(
            tip=data['quote'],
            source='API Ninjas'
        )
        return tip
    except Exception as e:
        print(f"Error fetching health tip: {e}")
        return None

def get_daily_health_tip():
    """Get today's health tip, fetching a new one if needed."""
    try:
        # Try to get today's tip
        tip = HealthTip.objects.latest('created_at')
        return tip
    except HealthTip.DoesNotExist:
        # If no tip exists, fetch a new one
        return fetch_health_tip()

def get_random_health_tip():
    """
    Get a random health tip from our database
    """
    try:
        return HealthTip.objects.order_by('?').first()
    except:
        return None 