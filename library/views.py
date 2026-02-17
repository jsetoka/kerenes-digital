import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.contrib.auth.decorators import login_required
from wagtail.documents import get_document_model

Document = get_document_model()


@login_required
def secure_download(request, doc_id: int):
    try:
        doc = Document.objects.get(id=doc_id)
    except Document.DoesNotExist:
        raise Http404()

    # Règles d’accès :
    # - si allowed_groups est vide -> tout utilisateur connecté
    # - sinon -> l’utilisateur doit être dans un des groupes
    allowed = doc.allowed_groups.all()
    if allowed.exists():
        user_groups = request.user.groups.all()
        if not allowed.filter(id__in=user_groups.values_list("id", flat=True)).exists():
            raise Http404()  # (ou 403, mais 404 évite d’énumérer)

    # Option : si confidential=True -> réserver aux staff
    if getattr(doc, "confidential", False) and not request.user.is_staff:
        raise Http404()

    file_path = os.path.join(settings.MEDIA_ROOT, doc.file.name)
    if not os.path.exists(file_path):
        raise Http404()

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename=os.path.basename(doc.file.name),
    )
