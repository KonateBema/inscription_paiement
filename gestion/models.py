from django.db import models


# ============================================================
# 1. ANNÉE ACADÉMIQUE
# ============================================================

class AnneeAcademique(models.Model):
    libelle = models.CharField(
        max_length=20,
        unique=True
    )

    date_debut = models.DateField(
        null=True,
        blank=True
    )

    date_fin = models.DateField(
        null=True,
        blank=True
    )

    active = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = "Année académique"
        verbose_name_plural = "Années académiques"
        ordering = ["-libelle"]

    def __str__(self):
        return self.libelle


# ============================================================
# 2. FILIÈRE
# ============================================================

class Filiere(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    nom = models.CharField(
        max_length=150
    )

    active = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"
        ordering = ["nom"]

    def __str__(self):
        return f"{self.code} - {self.nom}"


# ============================================================
# 3. NIVEAU
# ============================================================

class Niveau(models.Model):
    code = models.CharField(
        max_length=20,
        unique=True
    )

    nom = models.CharField(
        max_length=100
    )

    ordre = models.PositiveIntegerField(
        default=1
    )

    active = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"
        ordering = ["ordre"]

    def __str__(self):
        return self.nom


# ============================================================
# 4. CLASSE
# ============================================================

class Classe(models.Model):
    nom = models.CharField(
        max_length=150
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.PROTECT,
        related_name="classes"
    )

    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name="classes"
    )

    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.PROTECT,
        related_name="classes"
    )

    capacite = models.PositiveIntegerField(
        default=60
    )

    active = models.BooleanField(
        default=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Classe"
        verbose_name_plural = "Classes"
        ordering = ["filiere", "niveau", "nom"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "nom",
                    "filiere",
                    "niveau",
                    "annee_academique",
                ],
                name="unique_classe_annee",
            )
        ]

    def __str__(self):
        return (
            f"{self.nom} - "
            f"{self.filiere.code} - "
            f"{self.niveau.nom} - "
            f"{self.annee_academique.libelle}"
        )

# ============================================================
# 5. CANDIDAT
# ============================================================

class Candidat(models.Model):

    SEXE_CHOICES = [
        ("M", "Masculin"),
        ("F", "Féminin"),
    ]

    matricule_candidat = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
    )

    nom = models.CharField(
        max_length=100
    )

    prenoms = models.CharField(
        max_length=150
    )

    sexe = models.CharField(
        max_length=1,
        choices=SEXE_CHOICES
    )

    date_naissance = models.DateField()

    lieu_naissance = models.CharField(
        max_length=150
    )

    nationalite = models.CharField(
        max_length=100,
        default="Ivoirienne"
    )

    photo = models.ImageField(
        upload_to="candidats/photos/",
        null=True,
        blank=True
    )

    telephone = models.CharField(
        max_length=30
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    adresse = models.CharField(
        max_length=255,
        blank=True
    )

    ville = models.CharField(
        max_length=100,
        blank=True
    )

    dernier_diplome = models.CharField(
        max_length=150,
        blank=True
    )

    serie_diplome = models.CharField(
        max_length=100,
        blank=True
    )

    annee_obtention = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    etablissement_origine = models.CharField(
        max_length=200,
        blank=True
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    actif = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Candidat"
        verbose_name_plural = "Candidats"
        ordering = ["nom", "prenoms"]

    def save(self, *args, **kwargs):

        if not self.matricule_candidat:
            annee = self.date_creation.year if self.date_creation else None

            if not annee:
                from datetime import datetime
                annee = datetime.now().year

            dernier = Candidat.objects.filter(
                matricule_candidat__startswith=f"CAND-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.matricule_candidat.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.matricule_candidat = (
                f"CAND-{annee}-{numero:05d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.matricule_candidat} - "
            f"{self.nom} {self.prenoms}"
        )


# ============================================================
# 6. PRÉINSCRIPTION
# ============================================================

class Preinscription(models.Model):

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("DOSSIER_INCOMPLET", "Dossier incomplet"),
        ("DOSSIER_COMPLET", "Dossier complet"),
        ("VALIDEE", "Validée"),
        ("REJETEE", "Rejetée"),
    ]

    numero = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    candidat = models.ForeignKey(
        Candidat,
        on_delete=models.PROTECT,
        related_name="preinscriptions"
    )

    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.PROTECT,
        related_name="preinscriptions"
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.PROTECT,
        related_name="preinscriptions"
    )

    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name="preinscriptions"
    )

    statut = models.CharField(
        max_length=30,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE"
    )

    date_demande = models.DateTimeField(
        auto_now_add=True
    )

    date_traitement = models.DateTimeField(
        null=True,
        blank=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Préinscription"
        verbose_name_plural = "Préinscriptions"
        ordering = ["-date_demande"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "candidat",
                    "annee_academique",
                ],
                name="unique_preinscription_candidat_annee"
            )
        ]

    def save(self, *args, **kwargs):

        if not self.numero:
            annee = self.annee_academique.libelle

            dernier = Preinscription.objects.filter(
                numero__startswith=f"PRE-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.numero.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.numero = (
                f"PRE-{annee}-{numero:05d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.numero} - "
            f"{self.candidat.nom} {self.candidat.prenoms}"
        )

# ============================================================
# 7. ÉTUDIANT
# ============================================================

class Etudiant(models.Model):

    matricule = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    candidat = models.OneToOneField(
        Candidat,
        on_delete=models.PROTECT,
        related_name="etudiant"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    actif = models.BooleanField(
        default=True
    )

    class Meta:
        verbose_name = "Étudiant"
        verbose_name_plural = "Étudiants"
        ordering = ["matricule"]

    def save(self, *args, **kwargs):

        if not self.matricule:
            annee = self.date_creation.year if self.date_creation else None

            if not annee:
                from datetime import datetime
                annee = datetime.now().year

            dernier = Etudiant.objects.filter(
                matricule__startswith=f"ETU-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.matricule.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.matricule = f"ETU-{annee}-{numero:05d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.matricule} - "
            f"{self.candidat.nom} {self.candidat.prenoms}"
        )


# ============================================================
# 8. INSCRIPTION
# ============================================================
class Inscription(models.Model):

    TYPE_CHOICES = [
        ("PREMIERE_INSCRIPTION", "Première inscription"),
        ("REINSCRIPTION", "Réinscription"),
    ]

    STATUT_CHOICES = [
        ("EN_ATTENTE", "En attente"),
        ("INSCRIT", "Inscrit"),
        ("ANNULE", "Annulé"),
    ]

    MODE_PAIEMENT_CHOICES = [
        ("UNE_TRANCHE", "Une seule tranche"),
        ("DEUX_TRANCHES", "Deux tranches"),
    ]

    numero = models.CharField(
        max_length=30,
        unique=True,
        editable=False
    )

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.PROTECT,
        related_name="inscriptions"
    )

    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.PROTECT,
        related_name="inscriptions"
    )

    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.PROTECT,
        related_name="inscriptions"
    )

    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.PROTECT,
        related_name="inscriptions"
    )

    classe = models.ForeignKey(
        Classe,
        on_delete=models.PROTECT,
        related_name="inscriptions"
    )

    type_inscription = models.CharField(
        max_length=30,
        choices=TYPE_CHOICES,
        default="PREMIERE_INSCRIPTION"
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="EN_ATTENTE"
    )

    # =====================================================
    # FRAIS D'INSCRIPTION
    # =====================================================

    montant_inscription = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0,
        verbose_name="Frais d'inscription"
    )

    mode_paiement_inscription = models.CharField(
        max_length=20,
        choices=MODE_PAIEMENT_CHOICES,
        default="UNE_TRANCHE",
        verbose_name="Mode de paiement"
    )

    date_inscription = models.DateTimeField(
        auto_now_add=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        ordering = ["-date_inscription"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "etudiant",
                    "annee_academique",
                ],
                name="unique_inscription_etudiant_annee"
            )
        ]

    def save(self, *args, **kwargs):

        if not self.numero:

            annee = self.annee_academique.libelle

            dernier = Inscription.objects.filter(
                numero__startswith=f"INS-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.numero.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.numero = f"INS-{annee}-{numero:05d}"

        super().save(*args, **kwargs)
        
    @property
    def montant_inscription_paye(self):

        from django.db.models import Sum

        total = self.paiements_inscription.filter(
            statut="VALIDE"
        ).aggregate(
            total=Sum("montant")
        )["total"] or 0

        return min(
            total,
            self.montant_inscription
        )

    @property
    def reste_inscription_a_payer(self):

        return max(
            self.montant_inscription
            - self.montant_inscription_paye,
            0
        )

    @property
    def inscription_soldee(self):

        return self.reste_inscription_a_payer <= 0

    @property
    def pourcentage_inscription_paye(self):

        if self.montant_inscription <= 0:
            return 100

        return int(
            (
                self.montant_inscription_paye
                / self.montant_inscription
            ) * 100
        )   

    def __str__(self):

        return (
            f"{self.numero} - "
            f"{self.etudiant.matricule} - "
            f"{self.annee_academique.libelle}"
        )
        
# ============================================================
# 9. SCOLARITÉ
# ============================================================

class Scolarite(models.Model):

    STATUT_CHOICES = [
        ("NON_PAYEE", "Non payée"),
        ("PARTIELLEMENT_PAYEE", "Partiellement payée"),
        ("SOLDEE", "Soldée"),
    ]

    inscription = models.OneToOneField(
        Inscription,
        on_delete=models.PROTECT,
        related_name="scolarite"
    )

    montant_total = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    remise = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    montant_net = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        editable=False
    )

    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    reste_a_payer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    statut = models.CharField(
        max_length=30,
        choices=STATUT_CHOICES,
        default="NON_PAYEE"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True
    )

    date_modification = models.DateTimeField(
        auto_now=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Scolarité"
        verbose_name_plural = "Scolarités"
        ordering = ["-date_creation"]

    def save(self, *args, **kwargs):
        self.montant_net = self.montant_total - self.remise

        if self.montant_net < 0:
            self.montant_net = 0

    # Si l'objet existe déjà, on recalcule le montant payé
    # à partir des paiements valides.
        if self.pk:
           from django.db.models import Sum

           total_paye = self.paiements.filter(
            statut="VALIDE"
           ).aggregate(
            total=Sum("montant")
           )["total"] or 0

           self.montant_paye = total_paye

        if self.montant_paye >= self.montant_net:
           self.montant_paye = self.montant_net
           self.reste_a_payer = 0
           self.statut = "SOLDEE"

        elif self.montant_paye > 0:
             self.reste_a_payer = (
             self.montant_net - self.montant_paye
          )
             self.statut = "PARTIELLEMENT_PAYEE"

        else:
             self.montant_paye = 0
             self.reste_a_payer = self.montant_net
             self.statut = "NON_PAYEE"

        super().save(*args, **kwargs)
    
    def __str__(self):
        return (
            f"{self.inscription.etudiant.matricule} - "
            f"{self.inscription.annee_academique.libelle}"
        )

# ============================================================
# 10. ÉCHÉANCE
# ============================================================

class Echeance(models.Model):

    STATUT_CHOICES = [
        ("A_VENIR", "À venir"),
        ("EN_COURS", "En cours"),
        ("PAYEE", "Payée"),
        ("EN_RETARD", "En retard"),
    ]

    scolarite = models.ForeignKey(
        Scolarite,
        on_delete=models.PROTECT,
        related_name="echeances"
    )

    numero = models.PositiveIntegerField()

    libelle = models.CharField(
        max_length=150
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    date_echeance = models.DateField()

    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    reste_a_payer = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        editable=False
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="A_VENIR"
    )

    class Meta:
        verbose_name = "Échéance"
        verbose_name_plural = "Échéances"
        ordering = ["numero"]

        constraints = [
            models.UniqueConstraint(
                fields=["scolarite", "numero"],
                name="unique_echeance_scolarite_numero"
            )
        ]

    def save(self, *args, **kwargs):

        if self.pk:
           from django.db.models import Sum

           total_paye = self.paiements.filter(
             statut="VALIDE"
            ).aggregate(
            total=Sum("montant")
            )["total"] or 0

           self.montant_paye = total_paye

        if self.montant_paye >= self.montant:
             self.montant_paye = self.montant
             self.reste_a_payer = 0
             self.statut = "PAYEE"

        elif self.montant_paye > 0:
             self.reste_a_payer = (
             self.montant - self.montant_paye
        )
             self.statut = "EN_COURS"

        else:
            self.montant_paye = 0
            self.reste_a_payer = self.montant
            self.statut = "A_VENIR"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.scolarite.inscription.etudiant.matricule} - "
            f"Échéance {self.numero} - "
            f"{self.montant} FCFA"
        )
        
# ============================================================
# 11. PAIEMENT
# ============================================================

class Paiement(models.Model):

    MODE_PAIEMENT_CHOICES = [
        ("ESPECES", "Espèces"),
        ("CHEQUE", "Chèque"),
        ("VIREMENT", "Virement bancaire"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("CARTE", "Carte bancaire"),
        ("AUTRE", "Autre"),
    ]

    STATUT_CHOICES = [
        ("VALIDE", "Validé"),
        ("ANNULE", "Annulé"),
    ]

    reference = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )

    scolarite = models.ForeignKey(
        Scolarite,
        on_delete=models.PROTECT,
        related_name="paiements"
    )

    echeance = models.ForeignKey(
        Echeance,
        on_delete=models.PROTECT,
        related_name="paiements",
        null=True,
        blank=True
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    mode_paiement = models.CharField(
        max_length=30,
        choices=MODE_PAIEMENT_CHOICES
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="VALIDE"
    )

    date_paiement = models.DateTimeField(
        auto_now_add=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ["-date_paiement"]

    def save(self, *args, **kwargs):

        if not self.reference:
            from datetime import datetime

            annee = datetime.now().year

            dernier = Paiement.objects.filter(
                reference__startswith=f"PAY-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.reference.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.reference = f"PAY-{annee}-{numero:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.reference} - "
            f"{self.scolarite.inscription.etudiant.matricule} - "
            f"{self.montant} FCFA"
        )
        
# ============================================================
# 12. REÇU
# ============================================================

class Recu(models.Model):

    numero = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )

    paiement = models.OneToOneField(
        Paiement,
        on_delete=models.PROTECT,
        related_name="recu"
    )

    date_emission = models.DateTimeField(
        auto_now_add=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:
        verbose_name = "Reçu"
        verbose_name_plural = "Reçus"
        ordering = ["-date_emission"]

    def save(self, *args, **kwargs):

        if not self.numero:
            from datetime import datetime

            annee = datetime.now().year

            dernier = Recu.objects.filter(
                numero__startswith=f"REC-{annee}-"
            ).order_by("-id").first()

            numero = 1

            if dernier:
                try:
                    numero = int(
                        dernier.numero.split("-")[-1]
                    ) + 1
                except (ValueError, IndexError):
                    numero = dernier.id + 1

            self.numero = f"REC-{annee}-{numero:06d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.numero} - "
            f"{self.paiement.reference}"
        )

# ============================================================
# 13. ÉCHÉANCE DES FRAIS D'INSCRIPTION
# ============================================================

# ============================================================
# ÉCHÉANCES DES FRAIS D'INSCRIPTION
# ============================================================

class EcheanceInscription(models.Model):

    TYPE_CHOICES = [
        ("TRANCHE_1", "Tranche 1"),
        ("TRANCHE_2", "Tranche 2"),
    ]

    STATUT_CHOICES = [
        ("NON_PAYEE", "Non payée"),
        ("PARTIELLE", "Partiellement payée"),
        ("PAYEE", "Payée"),
    ]

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.CASCADE,
        related_name="echeances_inscription"
    )

    type_tranche = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    montant_paye = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        default=0
    )

    date_echeance = models.DateField(
        null=True,
        blank=True
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="NON_PAYEE"
    )

    date_paiement = models.DateTimeField(
        null=True,
        blank=True
    )

    class Meta:

        verbose_name = "Échéance inscription"
        verbose_name_plural = "Échéances inscription"

        ordering = ["id"]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "inscription",
                    "type_tranche",
                ],
                name="unique_echeance_inscription_tranche"
            )
        ]

    @property
    def reste_a_payer(self):

        return max(
            self.montant - self.montant_paye,
            0
        )

    def mettre_a_jour(self):

        from django.db.models import Sum

        total = (
            self.paiements
            .filter(
                statut="VALIDE"
            )
            .aggregate(
                total=Sum("montant")
            )["total"]
            or 0
        )

        self.montant_paye = min(
            total,
            self.montant
        )

        dernier_paiement = (
            self.paiements
            .filter(
                statut="VALIDE"
            )
            .order_by("-date_paiement")
            .first()
        )

        if self.montant_paye <= 0:

            self.statut = "NON_PAYEE"
            self.date_paiement = None

        elif self.montant_paye < self.montant:

            self.statut = "PARTIELLE"

            if dernier_paiement:
                self.date_paiement = (
                    dernier_paiement.date_paiement
                )

        else:

            self.montant_paye = self.montant
            self.statut = "PAYEE"

            if dernier_paiement:
                self.date_paiement = (
                    dernier_paiement.date_paiement
                )

        self.save(
            update_fields=[
                "montant_paye",
                "statut",
                "date_paiement",
            ]
        )

    def __str__(self):

        return (
            f"{self.inscription.numero} - "
            f"{self.get_type_tranche_display()}"
        )


# ============================================================
# PAIEMENT DES FRAIS D'INSCRIPTION
# ============================================================

class PaiementInscription(models.Model):

    MODE_PAIEMENT_CHOICES = [
        ("ESPECES", "Espèces"),
        ("CHEQUE", "Chèque"),
        ("VIREMENT", "Virement bancaire"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("CARTE", "Carte bancaire"),
        ("AUTRE", "Autre"),
    ]

    STATUT_CHOICES = [
        ("VALIDE", "Validé"),
        ("ANNULE", "Annulé"),
    ]

    reference = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )

    inscription = models.ForeignKey(
        Inscription,
        on_delete=models.PROTECT,
        related_name="paiements_inscription"
    )

    echeance = models.ForeignKey(
        EcheanceInscription,
        on_delete=models.PROTECT,
        related_name="paiements"
    )

    montant = models.DecimalField(
        max_digits=12,
        decimal_places=0
    )

    mode_paiement = models.CharField(
        max_length=30,
        choices=MODE_PAIEMENT_CHOICES
    )

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="VALIDE"
    )

    date_paiement = models.DateTimeField(
        auto_now_add=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:

        verbose_name = "Paiement inscription"
        verbose_name_plural = "Paiements inscription"

        ordering = ["-date_paiement"]

    def save(self, *args, **kwargs):

        if not self.reference:

            from datetime import datetime

            annee = datetime.now().year

            dernier = (
                PaiementInscription.objects
                .filter(
                    reference__startswith=f"PIN-{annee}-"
                )
                .order_by("-id")
                .first()
            )

            numero = 1

            if dernier:

                try:

                    numero = (
                        int(
                            dernier.reference.split("-")[-1]
                        ) + 1
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    numero = dernier.id + 1

            self.reference = (
                f"PIN-{annee}-{numero:06d}"
            )

        super().save(*args, **kwargs)

        if self.echeance_id:

            self.echeance.mettre_a_jour()

    def __str__(self):

        return (
            f"{self.reference} - "
            f"{self.inscription.etudiant.matricule} - "
            f"{self.montant} FCFA"
        )


# ============================================================
# REÇU DES FRAIS D'INSCRIPTION
# ============================================================

class RecuInscription(models.Model):

    numero = models.CharField(
        max_length=40,
        unique=True,
        editable=False
    )

    paiement = models.OneToOneField(
        PaiementInscription,
        on_delete=models.PROTECT,
        related_name="recu"
    )

    date_emission = models.DateTimeField(
        auto_now_add=True
    )

    observation = models.TextField(
        blank=True
    )

    class Meta:

        verbose_name = "Reçu inscription"
        verbose_name_plural = "Reçus inscription"

        ordering = ["-date_emission"]

    def save(self, *args, **kwargs):

        if not self.numero:

            from datetime import datetime

            annee = datetime.now().year

            dernier = (
                RecuInscription.objects
                .filter(
                    numero__startswith=f"RIN-{annee}-"
                )
                .order_by("-id")
                .first()
            )

            numero = 1

            if dernier:

                try:

                    numero = (
                        int(
                            dernier.numero.split("-")[-1]
                        ) + 1
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    numero = dernier.id + 1

            self.numero = (
                f"RIN-{annee}-{numero:06d}"
            )

        super().save(*args, **kwargs)

    def __str__(self):

        return (
            f"{self.numero} - "
            f"{self.paiement.reference}"
        )
        
# ============================================================
# 14. PAIEMENT DES FRAIS D'INSCRIPTION
# ============================================================
# ============================================================
# 15. REÇU DES FRAIS D'INSCRIPTION
# ============================================================

