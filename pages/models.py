from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from .blocks import ServicesBlock, CardsBlock, CTABlock


class HomePage(Page):
    # HERO
    hero_title = models.CharField(max_length=120, blank=True)
    hero_subtitle = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    hero_cta_label = models.CharField(max_length=50, blank=True)
    hero_cta_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    hero_cta_url = models.URLField(blank=True)

    # SECTIONS DYNAMIQUES
    body = StreamField(
        [
            ("section_title", blocks.CharBlock(required=False, max_length=120)),
            ("rich_text", blocks.RichTextBlock()),
            # ⚠️ Renommé pour éviter le doublon "cta"
            ("cta_simple", blocks.StructBlock([
                ("title", blocks.CharBlock(required=False)),
                ("text", blocks.RichTextBlock(required=False)),
                ("label", blocks.CharBlock(required=False, max_length=50)),
                ("page", blocks.PageChooserBlock(required=False)),
                ("url", blocks.URLBlock(required=False)),
            ])),
            ("services", ServicesBlock()),
            ("cards", CardsBlock()),
            ("cta", CTABlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_title"),
            FieldPanel("hero_subtitle"),
            FieldPanel("hero_image"),
            FieldPanel("hero_cta_label"),
            PageChooserPanel("hero_cta_page"),
            FieldPanel("hero_cta_url"),
        ], heading="Bannière (Hero)"),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "pages.StandardPage",
        "pages.FormationsIndexPage",          # ✅ AJOUT ICI (catalogue)
        "blog.BlogIndexPage",
        "blog.BlogPage",
        "contact.ContactFormPage",
        "contact.DemandeFormationPage",
        "library.DocumentLibraryPage",
        "diagnostic.DiagnosticIAIndexPage",
    ]

    template = "pages/home_page.html"


class StandardPage(Page):
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    hero_alt = models.CharField(max_length=160, blank=True)
    show_toc = models.BooleanField(
        default=True, help_text="Afficher le sommaire automatique (H2)")

    intro = RichTextField(blank=True)
    body = StreamField(
        [
            ("paragraphe", blocks.RichTextBlock(features=[
             "h2", "bold", "italic", "link", "ol", "ul"])),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_image"),
            FieldPanel("hero_alt"),
            FieldPanel("show_toc"),
        ], heading="En-tête (Hero)"),
        FieldPanel("intro"),
        FieldPanel("body"),
    ]


class FormationsIndexPage(Page):
    template = "pages/formations_index_page.html"  # ✅ recommandé
    intro = StreamField(
        [
            ("paragraphe", blocks.RichTextBlock(features=[
             "h2", "h3", "bold", "italic", "link", "ol", "ul"])),
            ("image", ImageChooserBlock()),
        ],
        use_json_field=True,
        blank=True,
    )
    parent_page_types = ["pages.HomePage", "wagtailcore.Page"]  # ✅ au choix
    # ✅ seulement les formations dedans
    subpage_types = ["pages.FormationPage"]

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
        )
        return context


class FormationPage(Page):
    template = "pages/formation_page.html"  # ✅ tu l'as déjà

    parent_page_types = ["pages.FormationsIndexPage"]  # ✅ IMPORTANT
    subpage_types = []  # ✅ pas d'enfants

    duree = models.CharField(max_length=50)
    public_cible = models.CharField(max_length=255)

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
        ]
    )

    modalite = models.CharField(
        max_length=50,
        choices=[
            ("presentiel", "Présentiel"),
            ("distanciel", "Distanciel"),
            ("hybride", "Hybride"),
        ],
        default="presentiel"
    )

    # ✅ TARIFS
    prix_individuel = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: 150 000 FCFA"
    )

    prix_entreprise = models.CharField(
        max_length=50,
        blank=True,
        help_text="Ex: 2 200 000 FCFA ou Sur devis"
    )

    inclus = RichTextField(
        blank=True,
        help_text="Optionnel : ce qui est inclus (supports, attestation, coaching, etc.)"
    )

    # ✅ CTA
    cta_label = models.CharField(
        max_length=80,
        blank=True,
        default="Demander cette formation"
    )
    cta_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    cta_url = models.URLField(blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("niveau"),
            FieldPanel("duree"),
            FieldPanel("public_cible"),
            FieldPanel("modalite"),
        ], heading="Informations générales"),

        MultiFieldPanel([
            FieldPanel("prix_individuel"),
            FieldPanel("prix_entreprise"),
            FieldPanel("inclus"),
        ], heading="Tarification"),


        FieldPanel("objectif"),
        FieldPanel("prerequis"),
        FieldPanel("programme"),

        # ✅ Panneau CTA
        MultiFieldPanel([
            FieldPanel("cta_label"),
            PageChooserPanel("cta_page"),
            FieldPanel("cta_url"),
        ], heading="Bouton d’appel à l’action (CTA)"),
    ]
