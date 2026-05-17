from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Badge, UserBadge, PointHistory

@login_required
def badge_list(request):
    all_badges = Badge.objects.all().order_by('points_required')
    unlocked_badges = UserBadge.objects.filter(user=request.user).values_list('badge_id', flat=True)
    point_history = PointHistory.objects.filter(user=request.user).order_by('-date')[:20]
    
    return render(request, 'gamification/badge_list.html', {
        'all_badges': all_badges,
        'unlocked_badges': unlocked_badges,
        'point_history': point_history
    })
