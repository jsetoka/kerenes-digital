from wagtail.documents.forms import BaseDocumentForm


class CustomDocumentForm(BaseDocumentForm):
    class Meta(BaseDocumentForm.Meta):
        fields = BaseDocumentForm.Meta.fields + (
            "doc_type",
            "reference",
            "confidential",
        )
