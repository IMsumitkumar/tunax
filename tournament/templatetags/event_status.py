from django import template
from django.utils import timezone

register = template.Library()


@register.filter
def event_upcoming(date_event):
    return date_event > timezone.now()

@register.filter
def event_ended(date_event):
    return date_event < timezone.now()

@register.filter
def event_live(start_date_event, end_date_event):
    return start_date_event < timezone.now() < end_date_event

@register.filter
def event_today(date_event):
    event_date = date_event.date()
    today_date = timezone.now()
    return event_date == today_date.date()