from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    max_streak = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} (Level {self.level})"

    def update_streak(self):
        from datetime import date, timedelta
        today = date.today()
        if self.last_active_date == today:
            return
        
        if self.last_active_date == today - timedelta(days=1):
            self.streak += 1
        else:
            self.streak = 1
        
        if self.streak > self.max_streak:
            self.max_streak = self.streak
            
        self.last_active_date = today
        self.save()

    def add_points(self, points, reason="", request=None):
        self.update_streak()
        
        # Apply streak multiplier: +10% for every 5 days of streak (max 2x)
        multiplier = 1.0 + min(1.0, (self.streak // 5) * 0.1)
        final_points = int(points * multiplier)
        
        self.points += final_points
        old_level = self.level
        # Simple level up logic: every 100 points
        self.level = (self.points // 100) + 1
        self.save()
        
        from gamification.models import PointHistory, Badge, UserBadge
        from django.contrib import messages
        
        PointHistory.objects.create(user=self.user, points=final_points, reason=reason)
        
        if request:
            streak_msg = f" (Streak {self.streak}x Bonus!)" if self.streak > 1 else ""
            messages.success(request, f"+{final_points} points{streak_msg} : {reason}")
            if self.level > old_level:
                messages.info(request, f"Félicitations ! Vous avez atteint le niveau {self.level} !")
        
        # Check for new badges
        available_badges = Badge.objects.filter(points_required__lte=self.points)
        for badge in available_badges:
            ub, created = UserBadge.objects.get_or_create(user=self.user, badge=badge)
            if created and request:
                messages.warning(request, f"Nouveau badge débloqué : {badge.name} !")