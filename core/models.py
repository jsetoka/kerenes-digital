# core/models.py
from django.db import models
from wagtail.snippets.models import register_snippet
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.models import Page, Orderable
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey

LINK_HELP = "Laisse vide si tu choisis une page interne."


class LinkFields(models.Model):
    title = models.CharField(max_length=100)
    link_page = models.ForeignKey(
        Page, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    link_url = models.CharField(
        max_length=255, blank=True, help_text=LINK_HELP)

    class Meta:
        abstract = True

    @property
    def url(self):
        return self.link_page.url if self.link_page else self.link_url


@register_snippet
class Menu(ClusterableModel):
    name = models.CharField(max_length=50, unique=True)

    panels = [
        FieldPanel("name"),
        InlinePanel("items", label="Éléments du menu"),
    ]

    def __str__(self):
        return self.name


class MenuItem(Orderable, ClusterableModel, LinkFields):
    menu = ParentalKey(Menu, on_delete=models.CASCADE, related_name="items")

    show_children = models.BooleanField(default=True)

    VISIBILITY_CHOICES = [
        ("all", "Toujours visible"),
        ("auth", "Visible si connecté"),
        ("anon", "Visible si non connecté"),
    ]
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default="all",
        help_text="Contrôle l'affichage selon l'état de connexion",
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
        FieldPanel("show_children"),
        FieldPanel("visibility"),
        InlinePanel("children", label="Sous-liens"),
    ]


class SubMenuItem(Orderable, LinkFields):
    # parent: le MenuItem (qui doit être ClusterableModel)
    parent = ParentalKey(MenuItem, on_delete=models.CASCADE,
                         related_name="children")

    panels = [
        FieldPanel("title"),
        FieldPanel("link_page"),
        FieldPanel("link_url"),
    ]

    def __str__(self):
        return self.title
