from core.models import Notification

def notifications_context(request):
    notifications = []
    unread_notifications_count = 0
    if request.user.is_authenticated and hasattr(request.user, 'role'):
        if request.user.role == 'customer':
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
        elif request.user.role == 'admin':
            notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
            unread_notifications_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {
        'notifications': notifications,
        'unread_notifications_count': unread_notifications_count,
    }
