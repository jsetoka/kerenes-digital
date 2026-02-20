# contact/models.py

from django import forms
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.models import Page


class FormField(AbstractFormField):
    page = ParentalKey(
        "contact.ContactFormPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class ConsentFormBuilder(FormBuilder):
    """
    Ajoute un champ 'consent' à la fin du formulaire.
    """

    def get_form_fields(self):
        fields = super().get_form_fields()
        # On laisse FormBuilder construire le reste, puis on ajoute 'consent'
        fields["consent"] = forms.BooleanField(
            label="",  # on affichera le texte depuis la page (consent_text)
            required=self.page.consent_required,
        )
        return fields


class ContactFormPage(AbstractEmailForm):
    template = "contact/contact_form_page.html"
    thank_you_text = RichTextField(
        blank=True, help_text="Texte affiché après envoi réussi.")

    # Réglages emails
    to_address = models.CharField(
        max_length=255, blank=True,
        help_text="Destinataire(s) de notification, séparés par des virgules."
    )
    from_address = models.CharField(
        max_length=255, blank=True, help_text="Adresse expéditrice")
    subject = models.CharField(
        max_length=255, blank=True, help_text="Sujet du mail de notification")

    # Consentement
    consent_text = RichTextField(
        blank=True,
        help_text="Message de consentement affiché sous les champs (ex. RGPD/marketing)."
    )
    consent_required = models.BooleanField(
        default=True,
        verbose_name="Consentement obligatoire",
        help_text="Si activé, la case doit être cochée pour soumettre le formulaire."
    )

    content_panels = Page.content_panels + [
        FieldPanel("thank_you_text"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("to_address"),
                        FieldPanel("from_address"),
                    ]
                ),
                FieldPanel("subject"),
            ],
            heading="Paramètres e-mail",
        ),
        MultiFieldPanel(
            [
                FieldPanel("consent_text"),
                FieldPanel("consent_required"),
            ],
            heading="Consentement",
        ),
    ]

    # Utilise notre builder qui ajoute 'consent'
    def get_form_class(self):
        fb = ConsentFormBuilder(self.form_fields.all())
        # Fournir la page au builder pour connaître consent_required
        fb.page = self
        return fb.get_form_class()


class DemandeFormationFormField(AbstractFormField):
    page = ParentalKey(
        "contact.DemandeFormationPage",
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


class DemandeFormationPage(AbstractEmailForm):
    template = "contact/demande_formation_page.html"
    landing_page_template = "contact/demande_formation_page_landing.html"

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

    # 🔹 Seulement le contexte — plus de logique RDV
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        formation_id = request.GET.get("formation_id")
        formation_title = None

        if formation_id:
            try:
                formation_page = Page.objects.get(
                    id=int(formation_id)).specific
                formation_title = formation_page.title
            except:
                formation_title = None

        context["formation_title"] = formation_title
        return context
