# library/permissions.py
from django.contrib.auth.models import AnonymousUser


def user_can_access_document(doc, user) -> bool:
    """
    Règles :
    - si doc.confidential=True -> staff seulement
    - si allowed_groups vide -> tout utilisateur connecté
    - sinon -> user doit appartenir à au moins un groupe autorisé
    """
    if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False

    # confidentiel => staff uniquement
    if getattr(doc, "confidential", False) and not user.is_staff:
        return False

    allowed = getattr(doc, "allowed_groups", None)
    if allowed is None:
        # si doc n'a pas le champ (fallback)
        return True

    if allowed.count() == 0:
        return True

    return user.groups.filter(id__in=allowed.values_list("id", flat=True)).exists()
