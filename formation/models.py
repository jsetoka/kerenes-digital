from django.core.exceptions import ValidationError
from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page


class FormationsIndexPage(Page):
    template = "formation/formations_index_page.html"

    intro = StreamField(
        [
            (
                "paragraphe",
                blocks.RichTextBlock(
                    features=["h2", "h3", "bold", "italic", "link", "ol", "ul"]
                ),
            ),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    # ✅ Une index ne doit pas avoir elle-même en parent.
    # Mets ici ton vrai parent (ex: home.HomePage) si tu veux contraindre.
    parent_page_types = ["pages.HomePage", "wagtailcore.Page"]

    # ✅ Uniquement des pages Formation dans l'index
    subpage_types = ["formation.FormationPage"]

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        context["formations"] = (
            self.get_children()
            .live()
            .public()
            .specific()
            .order_by("path")
        )
        return context


class FormationPage(Page):
    template = "formation/formation_page.html"

    parent_page_types = ["formation.FormationsIndexPage"]
    subpage_types = []

    # ✅ Infos
    duree = models.CharField(max_length=50, blank=True)
    public_cible = models.CharField(max_length=255, blank=True)

    objectif = RichTextField(blank=True)
    prerequis = RichTextField(blank=True)
    programme = RichTextField(blank=True)

    niveau = models.CharField(
        max_length=50,
        choices=[
            ("decouverte", "Découverte"),
            ("pratique", "Pratique"),
            ("technique", "Technique"),
            ("expert", "Expert"),
        ],
        default="decouverte",
    )

    modalite = models.CharField(
        max_length=50,
        choices=[
            ("presentiel", "Présentiel"),
            ("distanciel", "Distanciel"),
            ("hybride", "Hybride"),
        ],
        default="presentiel",
    )

    # ✅ Tarifs
    prix_individuel = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: 150 000 FCFA",
    )
    prix_entreprise = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: 2 200 000 FCFA ou Sur devis",
    )
    inclus = RichTextField(
        blank=True,
        help_text="Optionnel : supports, attestation, coaching, etc.",
    )

    # ✅ CTA
    cta_label = models.CharField(
        max_length=80,
        blank=True,
        default="Demander cette formation",
    )
    cta_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    cta_url = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("niveau"),
                FieldPanel("duree"),
                FieldPanel("public_cible"),
                FieldPanel("modalite"),
            ],
            heading="Informations générales",
        ),
        MultiFieldPanel(
            [
                FieldPanel("prix_individuel"),
                FieldPanel("prix_entreprise"),
                FieldPanel("inclus"),
            ],
            heading="Tarification",
        ),
        FieldPanel("objectif"),
        FieldPanel("prerequis"),
        FieldPanel("programme"),
        MultiFieldPanel(
            [
                FieldPanel("cta_label"),
                PageChooserPanel("cta_page"),
                FieldPanel("cta_url"),
            ],
            heading="Bouton d’appel à l’action (CTA)",
        ),
    ]

    def clean(self):
        super().clean()

        # ✅ Evite un CTA "mort"
        if self.cta_label and not (self.cta_page or self.cta_url):
            raise ValidationError(
                {"cta_url": "Renseigne une page (cta_page) ou une URL (cta_url) pour le CTA."}
            )

        # ✅ Evite d'avoir les 2 (optionnel, mais souvent mieux)
        if self.cta_page and self.cta_url:
            raise ValidationError(
                {"cta_url": "Choisis soit une page (cta_page), soit une URL (cta_url), pas les deux."}
            )
