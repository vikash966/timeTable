from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


from ..models import TimeSlot



@register.filter
def is_available(room, weekday, start_hour):
    return not TimeSlot.objects.filter(room=room, weekday=weekday, start_hour=start_hour, is_booked=True).exists()



@register.filter
def get_nested_value(dictionary, keys, default=None):
    try:
        keys = keys.split('.')
        for key in keys:
            dictionary = dictionary.get(key, {})
    except AttributeError:
        dictionary = {}
    return dictionary or default

@register.filter
def get_room_ids(booked_rooms):
    return [room['id'] for room in booked_rooms]


@register.filter
def remaining_slots(subject_id, booked_slots_count, subject_credits):
    return subject_credits - booked_slots_count