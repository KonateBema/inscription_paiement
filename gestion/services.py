from decimal import Decimal

from django.db import transaction
from django.db.models import Sum

from .models import Paiement, Scolarite, Echeance, Recu


@transaction.atomic
def enregistrer_paiement(
    scolarite,
    montant,
    mode_paiement,
    echeance=None,
    observation=""
):
    """
    Enregistre un paiement de manière sécurisée.

    Le paiement est enregistré dans une transaction atomique,
    puis la scolarité et l'échéance sont recalculées.
    """

    montant = Decimal(str(montant))

    # ========================================================
    # 1. VALIDATION DU MONTANT
    # ========================================================

    if montant <= 0:
        raise ValueError(
            "Le montant du paiement doit être supérieur à 0."
        )

    # ========================================================
    # 2. CALCUL DU RESTE DE LA SCOLARITÉ
    # ========================================================

    total_paye = (
        Paiement.objects
        .filter(
            scolarite=scolarite,
            statut="VALIDE"
        )
        .aggregate(
            total=Sum("montant")
        )["total"] or Decimal("0")
    )

    reste_scolarite = (
        scolarite.montant_net - total_paye
    )

    if montant > reste_scolarite:
        raise ValueError(
            f"Le montant dépasse le reste à payer "
            f"de {reste_scolarite} FCFA."
        )

    # ========================================================
    # 3. VÉRIFICATION DE L'ÉCHÉANCE
    # ========================================================

    if echeance is not None:

        if echeance.scolarite_id != scolarite.id:
            raise ValueError(
                "L'échéance ne correspond pas à cette scolarité."
            )

        total_echeance = (
            Paiement.objects
            .filter(
                echeance=echeance,
                statut="VALIDE"
            )
            .aggregate(
                total=Sum("montant")
            )["total"] or Decimal("0")
        )

        reste_echeance = (
            echeance.montant - total_echeance
        )

        if montant > reste_echeance:
            raise ValueError(
                f"Le montant dépasse le reste de "
                f"l'échéance : {reste_echeance} FCFA."
            )

    # ========================================================
    # 4. CRÉATION DU PAIEMENT
    # ========================================================

    paiement = Paiement.objects.create(
        scolarite=scolarite,
        echeance=echeance,
        montant=montant,
        mode_paiement=mode_paiement,
        statut="VALIDE",
        observation=observation,
    )

    # ========================================================
    # 5. RECALCUL DE LA SCOLARITÉ
    # ========================================================

    total_paye = (
        Paiement.objects
        .filter(
            scolarite=scolarite,
            statut="VALIDE"
        )
        .aggregate(
            total=Sum("montant")
        )["total"] or Decimal("0")
    )

    scolarite.montant_paye = total_paye

    scolarite.montant_net = (
        scolarite.montant_total - scolarite.remise
    )

    if scolarite.montant_net < 0:
        scolarite.montant_net = Decimal("0")

    if total_paye >= scolarite.montant_net:
        scolarite.montant_paye = scolarite.montant_net
        scolarite.reste_a_payer = Decimal("0")
        scolarite.statut = "SOLDEE"

    elif total_paye > 0:
        scolarite.reste_a_payer = (
            scolarite.montant_net - total_paye
        )
        scolarite.statut = "PARTIELLEMENT_PAYEE"

    else:
        scolarite.reste_a_payer = scolarite.montant_net
        scolarite.statut = "NON_PAYEE"

    scolarite.save()

    # ========================================================
    # 6. RECALCUL DE L'ÉCHÉANCE
    # ========================================================

    if echeance is not None:

        total_echeance = (
            Paiement.objects
            .filter(
                echeance=echeance,
                statut="VALIDE"
            )
            .aggregate(
                total=Sum("montant")
            )["total"] or Decimal("0")
        )

        echeance.montant_paye = total_echeance

        if total_echeance >= echeance.montant:
            echeance.montant_paye = echeance.montant
            echeance.reste_a_payer = Decimal("0")
            echeance.statut = "PAYEE"

        elif total_echeance > 0:
            echeance.reste_a_payer = (
                echeance.montant - total_echeance
            )
            echeance.statut = "EN_COURS"

        else:
            echeance.reste_a_payer = echeance.montant
            echeance.statut = "A_VENIR"

        echeance.save()

    # ========================================================
    # 7. CRÉATION DU REÇU
    # ========================================================

    recu = Recu.objects.create(
        paiement=paiement
    )

    return paiement, recu