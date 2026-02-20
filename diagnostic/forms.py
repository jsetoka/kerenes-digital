# diagnostic/forms.py
from django import forms


class DiagnosticCompletForm(forms.Form):
    SECTEUR = [
        ("0", "Administration publique"),
        ("1", "PME services"),
        ("2", "Industrie / BTP"),
        ("2", "Commerce / distribution"),
        ("3", "Banque / assurance / finance"),
        ("1", "Éducation / université"),
        ("1", "Autre"),
    ]
    # NOTE: ici j’ai volontairement mis des scores “par défaut” par secteur.
    # Tu peux les mettre tous à "1" si tu veux un scoring neutre.
    # L’idée est surtout de garder un format "0..3".

    Q7 = [
        ("0", "1 personne"),
        ("1", "2 à 5"),
        ("2", "6 à 20"),
        ("3", "Toute une équipe"),
    ]
    Q8 = [
        ("0", "Aucun impact"),
        ("1", "Retards"),
        ("2", "Pertes financières / problèmes clients"),
        ("3", "Risque majeur pour l’activité"),
    ]
    Q9 = [
        ("3", "Papier"),
        ("2", "Excel isolés"),
        ("1", "Plusieurs logiciels non connectés"),
        ("0", "Système centralisé"),
    ]
    Q10 = [
        ("0", "Jamais"),
        ("1", "Rarement"),
        ("2", "Plusieurs fois"),
        ("3", "Régulièrement"),
    ]
    Q11 = [
        ("3", "Inexistante"),
        ("2", "Utilisée individuellement (ChatGPT)"),
        ("1", "Testée dans certains services"),
        ("0", "Intégrée aux processus"),
    ]
    PRIORITE = [
        ("0", "Gain de temps des équipes"),
        ("1", "Réduction des coûts"),
        ("2", "Meilleures décisions"),
        ("2", "Augmenter le chiffre d’affaires"),
        ("1", "Améliorer la satisfaction client"),
    ]

    q6 = forms.ChoiceField(label="Secteur d’activité",
                           choices=SECTEUR, widget=forms.RadioSelect)
    q7 = forms.ChoiceField(
        label="Combien de personnes font des tâches répétitives ?", choices=Q7, widget=forms.RadioSelect)
    q8 = forms.ChoiceField(
        label="Une erreur de données peut entraîner…", choices=Q8, widget=forms.RadioSelect)
    q9 = forms.ChoiceField(
        label="Vos informations sont stockées surtout dans…", choices=Q9, widget=forms.RadioSelect)
    q10 = forms.ChoiceField(
        label="Données perdues / mauvaise version ?", choices=Q10, widget=forms.RadioSelect)
    q11 = forms.ChoiceField(
        label="L’IA est aujourd’hui dans l’organisation…", choices=Q11, widget=forms.RadioSelect)
    q12 = forms.ChoiceField(label="Votre priorité business",
                            choices=PRIORITE, widget=forms.RadioSelect)

    def clean(self):
        cleaned = super().clean()
        cleaned["q6_label"] = dict(self.SECTEUR).get(cleaned.get("q6"), "")
        cleaned["q12_label"] = dict(self.PRIORITE).get(cleaned.get("q12"), "")
        return cleaned


class DiagnosticExpressForm(forms.Form):
    # On stocke 0..3 pour le score + un label pour exploitation commerciale
    Q1_CHOICES = [
        ("0", "1–10 employés"),
        ("1", "11–50 employés"),
        ("2", "51–200 employés"),
        ("3", "200+ employés"),
    ]
    Q2_CHOICES = [
        ("0", "Aucun / très faible"),
        ("1", "Modéré"),
        ("2", "Élevé"),
        ("3", "Très élevé"),
    ]
    Q3_CHOICES = [
        ("0", "Jamais"),
        ("1", "Parfois"),
        ("2", "Souvent"),
        ("3", "Très souvent"),
    ]
    Q4_CHOICES = [
        ("0", "Immédiat"),
        ("1", "Parfois long"),
        ("2", "Souvent long"),
        ("3", "Très difficile"),
    ]

    q1 = forms.ChoiceField(label="Taille de l’organisation",
                           choices=Q1_CHOICES, widget=forms.RadioSelect)
    q2 = forms.ChoiceField(label="Temps perdu en tâches répétitives",
                           choices=Q2_CHOICES, widget=forms.RadioSelect)
    q3 = forms.ChoiceField(label="Décisions sans indicateurs fiables",
                           choices=Q3_CHOICES, widget=forms.RadioSelect)
    q4 = forms.ChoiceField(label="Retrouver une information interne",
                           choices=Q4_CHOICES, widget=forms.RadioSelect)

    # Pour garder des labels exploitables côté DB (facultatif mais pratique)
    def clean(self):
        cleaned = super().clean()
        # labels
        labels = dict(self.Q1_CHOICES)
        cleaned["q1_label"] = labels.get(cleaned.get("q1"), "")
        return cleaned


class DiagnosticContactForm(forms.Form):
    nom = forms.CharField(label="Nom", max_length=120)
    email = forms.EmailField(label="Email professionnel")
    telephone = forms.CharField(
        label="Téléphone / WhatsApp (optionnel)", max_length=40, required=False)


class PlanActionForm(forms.Form):
    objectif = forms.CharField(required=False)
    probleme_principal = forms.CharField(max_length=160)
    outils_actuels = forms.CharField(required=False, max_length=160)
