from django import forms


SECTEURS = [
    ("public", "Administration publique"),
    ("pme_services", "PME services"),
    ("industrie_btp", "Industrie / BTP"),
    ("commerce", "Commerce / distribution"),
    ("banque", "Banque / finance / assurance"),
    ("education", "Éducation / université"),
    ("autre", "Autre"),
]

TAILLES = [
    ("1_10", "1–10 employés"),
    ("11_50", "11–50"),
    ("51_200", "51–200"),
    ("200_plus", "200+"),
]

FONCTIONS = [
    ("dirigeant", "Dirigeant / DG"),
    ("manager", "Manager / Chef service"),
    ("ingenieur", "Ingénieur / analyste"),
    ("rh_admin", "RH / administratif"),
    ("it", "IT / informatique"),
]

URGENCE = [
    ("faible", "Faible"),
    ("moyenne", "Moyenne"),
    ("elevee", "Élevée"),
]

DONNEES = [
    ("dispersees", "Dispersées (Excel/WhatsApp/PC)"),
    ("partielles", "Partielles (quelques outils)"),
    ("structurees", "Structurées (CRM/ERP/BI)"),
    ("avancees", "Avancées (Datawarehouse / gouvernance)"),
]


class ExpressDiagnosticForm(forms.Form):
    q1_secteur = forms.ChoiceField(
        label="Secteur d’activité", choices=SECTEURS, widget=forms.RadioSelect)
    q2_taille = forms.ChoiceField(
        label="Taille de l’organisation", choices=TAILLES, widget=forms.RadioSelect)
    q3_fonction = forms.ChoiceField(
        label="Votre fonction", choices=FONCTIONS, widget=forms.RadioSelect)
    q4_urgence = forms.ChoiceField(
        label="Urgence d’améliorer performance/coûts ?", choices=URGENCE, widget=forms.RadioSelect)
    q5_donnees = forms.ChoiceField(
        label="État actuel de vos données", choices=DONNEES, widget=forms.RadioSelect)


CRENEAUX = [
    ("lun_10_12", "Lundi 10h–12h"),
    ("lun_14_16", "Lundi 14h–16h"),
    ("mar_10_12", "Mardi 10h–12h"),
    ("mar_14_16", "Mardi 14h–16h"),
    ("mer_10_12", "Mercredi 10h–12h"),
    ("jeu_14_16", "Jeudi 14h–16h"),
    ("ven_10_12", "Vendredi 10h–12h"),
]

CANAL = [
    ("appel", "Appel"),
    ("whatsapp", "WhatsApp"),
    ("visio", "Visio"),
]


class RdvRequestForm(forms.Form):
    nom = forms.CharField(label="Nom", max_length=120, required=False)
    email = forms.EmailField(label="Email", required=False)
    telephone = forms.CharField(
        label="Téléphone *", max_length=40, required=True)

    creneau = forms.ChoiceField(
        label="Créneau préféré",
        choices=CRENEAUX,
        widget=forms.RadioSelect,
        required=True,
    )
    canal = forms.ChoiceField(
        label="Canal",
        choices=CANAL,
        widget=forms.RadioSelect,
        initial="appel",
        required=True,
    )
    besoin = forms.CharField(
        label="Besoin (optionnel)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )


RISQUE = [
    ("faible", "Faible"),
    ("moyen", "Moyen"),
    ("eleve", "Élevé"),
]

PERTES = [
    ("0_1", "0–1M FCFA / mois"),
    ("1_5", "1–5M FCFA / mois"),
    ("5_20", "5–20M FCFA / mois"),
    ("20_plus", "20M+ / mois"),
]

STOCKAGE = [
    ("whatsapp_excel", "WhatsApp / Excel / PC dispersés"),
    ("drive", "Google Drive / OneDrive (partagé)"),
    ("crm_erp", "CRM/ERP (structuré)"),
    ("dwh", "Datawarehouse / gouvernance data"),
]

USAGE_IA = [
    ("aucun", "Aucun"),
    ("ponctuel", "Ponctuel (essais / outils IA)"),
    ("regulier", "Régulier (quelques cas d’usage)"),
    ("industrialise", "Industrialisé (process / MLOps / KPI)"),
]

OBJECTIF = [
    ("reduction_couts", "Réduction des coûts"),
    ("gain_temps", "Gain de temps / automatisation"),
    ("meilleure_decision", "Meilleure décision (pilotage)"),
    ("croissance", "Croissance / ventes"),
    ("qualite", "Qualité / conformité / risques"),
]

REPORTING = [
    ("quotidien", "Quotidien"),
    ("hebdo", "Hebdomadaire"),
    ("mensuel", "Mensuel"),
    ("rare", "Rare / au besoin"),
]

PRIORITE = [
    ("vente_marketing", "Vente / marketing"),
    ("finance", "Finance / compta"),
    ("ops", "Opérations / production"),
    ("rh", "RH / administratif"),
    ("service_client", "Service client"),
]


class DiagnosticCompletForm(forms.Form):
    c1_risque_erreur = forms.ChoiceField(
        label="Risque d’erreur (décisions/ops)", choices=RISQUE, widget=forms.RadioSelect)
    c2_pertes = forms.ChoiceField(
        label="Pertes estimées liées aux inefficacités", choices=PERTES, widget=forms.RadioSelect)
    c3_stockage_data = forms.ChoiceField(
        label="Où sont stockées vos données ?", choices=STOCKAGE, widget=forms.RadioSelect)
    c4_usage_ia = forms.ChoiceField(
        label="Usage actuel de l’IA", choices=USAGE_IA, widget=forms.RadioSelect)
    c5_objectif = forms.ChoiceField(
        label="Objectif principal", choices=OBJECTIF, widget=forms.RadioSelect)
    c6_frequence_reporting = forms.ChoiceField(
        label="Fréquence de suivi / reporting", choices=REPORTING, widget=forms.RadioSelect)
    c7_priorite_process = forms.ChoiceField(
        label="Process prioritaire à améliorer", choices=PRIORITE, widget=forms.RadioSelect)
