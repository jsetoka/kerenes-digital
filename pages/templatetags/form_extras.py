from django import template
register = template.Library()

@register.filter
def widget_type(bound_field):
    try:
        return bound_field.field.widget.__class__.__name__
    except Exception:
        return ""

@register.filter
def is_checkbox(bound_field):
    return getattr(bound_field.field.widget, "input_type", "") == "checkbox"

@register.filter
def is_select(bound_field):
    wt = widget_type(bound_field)
    return wt in ("Select", "SelectMultiple", "SelectDateWidget")
