from core.models import Menu


def main_menu(request):
    try:
        menu = Menu.objects.prefetch_related(
            "items__children",
            "items__link_page",
            "items__children__link_page",
        ).get(name="main")

        items = []
        for item in menu.items.all():
            v = getattr(item, "visibility", "all")

            if v == "auth" and not request.user.is_authenticated:
                continue
            if v == "anon" and request.user.is_authenticated:
                continue

            items.append(item)

    except Menu.DoesNotExist:
        items = []

    return {"main_menu_items": items}
