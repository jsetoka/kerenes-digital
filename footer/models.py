from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField, RichTextField
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.images.blocks import ImageChooserBlock  # si un logo un jour


class LinkBlock(blocks.StructBlock):
    label = blocks.CharBlock(required=True, help_text="Texte du lien")
    page = blocks.PageChooserBlock(
        required=False, help_text="Lien vers une page interne")
    url = blocks.URLBlock(required=False, help_text="…ou URL externe")

    class Meta:
        icon = "link"
        label = "Lien"


class SocialBlock(blocks.StructBlock):
    label = blocks.CharBlock(
        required=True, help_text="Nom du réseau (Facebook, X/Twitter, LinkedIn…)")
    icon_class = blocks.CharBlock(
        required=False, help_text="Classe Bootstrap Icons (ex: bi bi-facebook)")
    url = blocks.URLBlock(required=True)

    class Meta:
        icon = "site"
        label = "Réseau social"


@register_setting
class FooterSettings(BaseSiteSetting):
    # Colonne 1
    about_title = models.CharField(max_length=100, default="À propos")
    about_text = RichTextField(features=["bold", "italic", "link", "h2", "h3", "h4", "h5", "h6", "left", "center", "right", "justify"], blank=True, default=(
        "Kerenes est un projet collaboratif visant à valoriser les talents et l’innovation au Congo."
    ))

    # Colonne 2
    links_title = models.CharField(max_length=100, default="Liens utiles")
    links = StreamField(
        [("link", LinkBlock())],
        use_json_field=True, blank=True, default=[]
    )

    # Colonne 3
    social_title = models.CharField(max_length=100, default="Suivez-nous")
    socials = StreamField(
        [("social", SocialBlock())],
        use_json_field=True, blank=True, default=[]
    )

    # Style (classes utilitaires Bootstrap/Tailwind selon ton stack)
    footer_bg_class = models.CharField(
        max_length=100, default="bg-navy",
        help_text="Classe CSS de fond (ex: bg-navy ou bg-dark)"
    )
    footer_text_class = models.CharField(
        max_length=100, default="text-light",
        help_text="Classe CSS du texte (ex: text-light)"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel("about_title"),
            FieldPanel("about_text"),
        ], heading="Colonne 1 : À propos"),
        MultiFieldPanel([
            FieldPanel("links_title"),
            FieldPanel("links"),
        ], heading="Colonne 2 : Liens utiles"),
        MultiFieldPanel([
            FieldPanel("social_title"),
            FieldPanel("socials"),
        ], heading="Colonne 3 : Réseaux sociaux"),
        MultiFieldPanel([
            FieldPanel("footer_bg_class"),
            FieldPanel("footer_text_class"),
        ], heading="Style"),
    ]

    class Meta:
        verbose_name = "Footer (paramètres du site)"
