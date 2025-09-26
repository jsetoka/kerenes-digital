from core.models import Menu

def main_menu(request):
    try:
        menu = Menu.objects.prefetch_related(
            "items__children", "items__link_page", "items__children__link_page"
        ).get(name="main")
        items = list(menu.items.all())
    except Menu.DoesNotExist:
        print("PAS DE MENU", flush=True)
        items = []
    return {"main_menu_items": items}


