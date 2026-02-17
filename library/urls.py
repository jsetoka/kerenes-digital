from django.urls import path
from .views import secure_download

urlpatterns = [
    path("download/<int:doc_id>/", secure_download, name="secure_download"),
]
