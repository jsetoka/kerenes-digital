def calcul_score_express(data: dict) -> int:
    score = 0

    score += {
        "dispersees": 5,
        "partielles": 10,
        "structurees": 20,
        "avancees": 25,
    }.get(data.get("q5_donnees"), 0)

    score += {
        "elevee": 20,
        "moyenne": 10,
        "faible": 5,
    }.get(data.get("q4_urgence"), 0)

    score += {
        "1_10": 5,
        "11_50": 10,
        "51_200": 15,
        "200_plus": 20,
    }.get(data.get("q2_taille"), 0)

    score += 15 if data.get("q3_fonction") == "dirigeant" else 5

    score += 10 if data.get("q1_secteur") in ["industrie_btp", "banque"] else 5

    return score


def niveau_et_gain(score: int) -> tuple[str, str]:
    if score < 40:
        return "critique", "+25% à +60% de productivité"
    if score < 70:
        return "intermediaire", "+15% à +35% de productivité"
    return "avance", "+5% à +20% d’optimisation"
