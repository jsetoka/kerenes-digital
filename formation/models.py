from django.core.exceptions import ValidationError
from django.db import models

from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField


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


class DemandeFormationFormField(AbstractFormField):
    page = ParentalKey(
        "formation.FormationRequestPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )

    panels = [
        FieldPanel("label"),
        FieldPanel("clean_name"),     # ✅ le “Nom interne”
        FieldPanel("field_type"),
        FieldPanel("required"),
        FieldPanel("choices"),
        FieldPanel("default_value"),
        FieldPanel("help_text"),
    ]


class FormationRequestPage(AbstractEmailForm):
    template = "formation/demande_page.html"
    landing_page_template = "formation/demande_landing_page.html"

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [
                InlinePanel("form_fields", label="Champs du formulaire"),
            ],
            heading="Formulaire",
        ),
        MultiFieldPanel(
            [
                FieldPanel("to_address"),
                FieldPanel("from_address"),
                FieldPanel("subject"),
            ],
            heading="Emails (réception)",
        ),
        FieldPanel("thank_you_text"),
    ]

    parent_page_types = ["pages.HomePage", "wagtailcore.Page"]
    subpage_types = []

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        formation_id = request.GET.get("formation_id")
        formation_title = None

        if formation_id:
            try:
                formation_page = (
                    FormationPage.objects
                    .live()
                    .public()
                    .get(id=int(formation_id))
                )
                formation_title = formation_page.title
            except (ValueError, FormationPage.DoesNotExist):
                formation_id = None
                formation_title = None

        context["formation_id"] = formation_id
        context["formation_title"] = formation_title
        return context
