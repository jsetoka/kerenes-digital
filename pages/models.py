from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, PageChooserPanel
from .blocks import ServicesBlock, CardsBlock, CTABlock


from wagtail.models import Page


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

    hero_promise = StreamField(
        [
            ("promise_card", blocks.StructBlock([
                ("icon", blocks.CharBlock(required=False, default="🚀")),
                ("title", blocks.CharBlock(required=True, max_length=120,
                 default="Votre performance commence par vos données")),
                ("text", blocks.TextBlock(required=False,
                 default="Nous construisons des systèmes mesurables et automatisés : du diagnostic jusqu’au déploiement.")),

                ("step_1_title", blocks.CharBlock(
                    required=False, default="Comprendre")),
                ("step_1_text", blocks.CharBlock(
                    required=False, default="audit & données")),

                ("step_2_title", blocks.CharBlock(
                    required=False, default="Construire")),
                ("step_2_text", blocks.CharBlock(
                    required=False, default="apps & outils")),

                ("step_3_title", blocks.CharBlock(
                    required=False, default="Automatiser")),
                ("step_3_text", blocks.CharBlock(
                    required=False, default="process & IA")),

                ("step_4_title", blocks.CharBlock(
                    required=False, default="Optimiser")),
                ("step_4_text", blocks.CharBlock(
                    required=False, default="KPI & perf")),

                ("button_label", blocks.CharBlock(
                    required=False, default="Demander un diagnostic")),
                ("button_page", blocks.PageChooserBlock(required=False)),
                ("button_url", blocks.URLBlock(required=False)),

                ("footnote", blocks.CharBlock(required=False,
                 default="Réponse rapide • Offre adaptée à votre contexte")),
            ])),
        ],
        use_json_field=True,
        blank=True,
        max_num=1
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
        FieldPanel("hero_promise"),
        FieldPanel("body"),
    ]

    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "pages.StandardPage",
        "formation.FormationsIndexPage",
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
