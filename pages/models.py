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
            ("cta", blocks.StructBlock([
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

    parent_page_types = ["wagtailcore.Page"]  # ou une RootPage personnalisée
    subpage_types = [
        "pages.StandardPage",
        "blog.BlogIndexPage",
        "blog.BlogPage",
        "contact.ContactFormPage",
        "library.DocumentLibraryPage",  # ✅ AJOUTE ÇA
    ]
    template = "pages/home_page.html"


class StandardPage(Page):
    template = "pages/standard_page.html"
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
        FieldPanel("intro"),
        FieldPanel("body"),
    ]
