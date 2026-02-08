from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel

from wagtail.snippets.models import register_snippet
from wagtail.documents.blocks import DocumentChooserBlock


class HomePage(Page):
    # Hero
    hero_title = models.CharField(max_length=255, default="Bienvenue")
    hero_video = models.URLField(
        blank=True, null=True, help_text="Lien vidéo YouTube/Vimeo")
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="+"
    )

    # Trois colonnes Vision / Gouvernance / Historique
    vision = RichTextField(blank=True)
    gouvernance = RichTextField(blank=True)
    historique = RichTextField(blank=True)

    # Services (grille 2x2)
    services = StreamField([
        ("service", blocks.StructBlock([
            ("nom", blocks.CharBlock(required=True)),
            ("lien", blocks.URLBlock(required=True)),
            ("image", ImageChooserBlock(required=False)),
        ]))
    ], blank=True, use_json_field=True)

    # Actualités (liées aux articles)
    # actualites = StreamField([
    #     ("article", blocks.StructBlock([
    #         ("titre", blocks.CharBlock(required=True)),
    #         ("resume", blocks.TextBlock(required=True)),
    #         ("lien", blocks.URLBlock(required=True)),
    #         ("image", ImageChooserBlock(required=False)),
    #     ]))
    # ], blank=True, use_json_field=True)

    # Ton StreamField d’actualités devient une liste de pages choisies
    actualites = StreamField(
        [
            ("actu", blocks.PageChooserBlock(target_model="blog.BlogPage")),
        ],
        use_json_field=True,
        blank=True,
    )

    # Bloc Média
    medias = StreamField([
        ("media", blocks.StructBlock([
            ("type", blocks.ChoiceBlock(choices=[
             ("photo", "Photo"), ("video", "Vidéo")])),
            ("fichier", ImageChooserBlock(required=False)),
            ("lien_video", blocks.URLBlock(required=False)),
        ]))
    ], blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("hero_title"),
            FieldPanel("hero_video"),
            FieldPanel("hero_image"),
        ], heading="Hero"),
        MultiFieldPanel([
            FieldPanel("vision"),
            FieldPanel("gouvernance"),
            FieldPanel("historique"),
        ], heading="Vision | Gouvernance | Historique"),
        FieldPanel("services"),
        FieldPanel("actualites"),
        FieldPanel("medias"),
    ]


class StandardPage(Page):
    Template = "pages/standard_page.html"
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
