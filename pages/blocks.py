# pages/blocks.py
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ServiceItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=80)
    description = blocks.TextBlock(required=False)
    icon = blocks.CharBlock(
        required=False,
        help_text="Classe icône (ex: fa-solid fa-gear) ou nom d’icône."
    )
    link_page = blocks.PageChooserBlock(required=False)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "cog"
        label = "Service"


class ServicesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, max_length=120, default="Nos services")
    intro = blocks.RichTextBlock(required=False)
    items = blocks.ListBlock(ServiceItemBlock(), min_num=1, max_num=12)

    class Meta:
        template = "blocks/services_block.html"
        icon = "list-ul"
        label = "Section Services"

# -----------------------------------------------------------------------


class CardItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=80)
    description = blocks.TextBlock(required=False)
    image = ImageChooserBlock(required=False)
    link_page = blocks.PageChooserBlock(required=False)
    link_url = blocks.URLBlock(required=False)

    class Meta:
        icon = "doc-full"
        label = "Carte"


class CardsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(
        required=False, max_length=120, default="Nos cartes")
    intro = blocks.RichTextBlock(required=False)
    items = blocks.ListBlock(CardItemBlock(), min_num=1, max_num=12)

    class Meta:
        template = "blocks/cards_block.html"
        icon = "placeholder"  # choisissez une icône adaptée
        label = "Section Cartes"


# -----------------------------------------------------------------------

class CTABlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, max_length=120)
    text = blocks.RichTextBlock(required=False)
    button_label = blocks.CharBlock(max_length=50, default="En savoir plus")
    page = blocks.PageChooserBlock(required=False)
    url = blocks.URLBlock(required=False)

    class Meta:
        template = "blocks/cta_block.html"
        icon = "placeholder"
        label = "CTA"
