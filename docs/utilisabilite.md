# Protocole de test d'utilisabilité (recette utilisateur)

Exigence : **QR-US-02** (cahier §6.4 « parcours utilisateur validé ») ; cas **UX-02** (réussite et temps des tâches)
et **UX-03** (satisfaction SUS). Caractéristiques : facilité d'utilisation (reconnaissabilité, facilité
d'apprentissage, exploitabilité, protection contre les erreurs) et qualité en utilisation (efficacité,
efficience, satisfaction) — Chapitre I.

Cibles (décision Q-12) : taux de réussite des tâches **>= 80 %** ; score SUS moyen **>= 68**.

> Règle d'or : aucun résultat ci-dessous n'est rempli à l'avance. Les notes brutes de chaque séance sont saisies
> telles quelles, puis les indicateurs sont **calculés par un script** (phase 8), jamais à la main.

## 1. Participants et organisation

- **Nombre** : 3 à 5 participants, n'ayant pas participé au développement.
- **Profils** : au moins un participant peu familier des boutiques en ligne ; idéalement un profil « personnel de
  vente » pour la tâche 3.
- **Durée** : 10 minutes par participant (2 min d'accueil, 6 min de tâches, 2 min de questionnaire).
- **Lieu** : en présentiel ou en visioconférence avec partage d'écran ; navigateur au choix du participant.
- **Environnement** : application lancée en local (`make db`, `make api`, `make web`), base de démonstration ;
  comptes prêts : un compte client neuf par participant, `staff@example.com` / `staff1234` pour la tâche 3.
- **Rôles** : un animateur (lit les consignes, ne guide pas) et un observateur (chronomètre, prend les notes).

## 2. Consentement (à lire au participant)

« Nous testons l'application, pas vous. Il n'y a pas de mauvaise réponse. Nous notons ce que vous faites et dites,
sans enregistrer votre image ni votre voix. Vos réponses restent anonymes (P1, P2…). Vous pouvez arrêter à tout
moment. Acceptez-vous de participer ? »

Consentement oral recueilli : ☐ oui — date, heure, identifiant du participant.

## 3. Tâches

Consigne générale : « Pensez à voix haute : dites ce que vous cherchez, ce que vous comprenez, ce qui vous
surprend. » L'animateur ne répond à aucune question sur l'interface pendant la tâche.

| Tâche | Consigne lue au participant | Critère de réussite (observable) | Temps maximal |
| --- | --- | --- | --- |
| T1 — Trouver et commander | « Trouvez un mug de moins de 20 € disponible en stock et commandez-en 2. » | Une commande au statut « Passée » contenant 2 mugs apparaît dans « Mes commandes » | 3 min |
| T2 — Corriger une erreur | « Ajoutez au panier plus d'exemplaires que le stock disponible d'un produit, puis faites en sorte que la commande passe. » | Le message de stock insuffisant est lu, la quantité est réduite, la commande est enregistrée | 3 min |
| T3 — Back-office | (compte personnel) « Passez la dernière commande à l'état "Expédiée", puis trouvez le chiffre d'affaires du jour. » | Statut « Expédiée » affiché ; montant du chiffre d'affaires lu à voix haute | 3 min |

Échec d'une tâche : critère non atteint, temps maximal dépassé, ou abandon. Aide de l'animateur = échec.

## 4. Mesures

- **Réussite** : 1 (réussie) ou 0 (échouée) par tâche et par participant.
- **Temps sur la tâche** : du dernier mot de la consigne jusqu'au critère de réussite (ou abandon), en secondes,
  au chronomètre.
- **Erreurs observées** : clics inutiles, retours en arrière, messages d'erreur rencontrés.
- **Verbatim** : phrases marquantes du « penser à voix haute ».
- **Satisfaction** : questionnaire SUS (§ 5).

## 5. Questionnaire SUS (System Usability Scale)

Réponse de 1 (pas du tout d'accord) à 5 (tout à fait d'accord).

1. Je pense que j'aimerais utiliser cette application fréquemment.
2. J'ai trouvé l'application inutilement complexe.
3. J'ai trouvé l'application facile à utiliser.
4. Je pense que j'aurais besoin de l'aide d'une personne technique pour utiliser cette application.
5. J'ai trouvé que les différentes fonctions de l'application étaient bien intégrées.
6. J'ai trouvé qu'il y avait trop d'incohérences dans l'application.
7. J'imagine que la plupart des gens apprendraient très rapidement à utiliser cette application.
8. J'ai trouvé l'application très lourde à utiliser.
9. Je me suis senti(e) très en confiance en utilisant l'application.
10. J'ai dû apprendre beaucoup de choses avant de pouvoir utiliser cette application.

**Calcul du score** (par participant) : pour les items impairs, contribution = réponse − 1 ; pour les items pairs,
contribution = 5 − réponse ; score SUS = somme des 10 contributions × 2,5 (de 0 à 100). Le score moyen est la
moyenne des scores des participants.

## 6. Grille de notes brutes (une par participant, à remplir pendant la séance)

| Participant | Tâche | Réussite (0/1) | Temps (s) | Erreurs observées | Verbatim |
| --- | --- | --- | --- | --- | --- |
| P1 | T1 | | | | |
| P1 | T2 | | | | |
| P1 | T3 | | | | |

| Participant | Q1 | Q2 | Q3 | Q4 | Q5 | Q6 | Q7 | Q8 | Q9 | Q10 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | | | | | | | | | | |

## 7. Résultats — **en attente**

> **Statut au 20/11/2026 : sessions en attente.** Décision du groupe (20/11/2026, 01:00) : les séances avec les
> participants ont lieu le 20/11/2026, avant la remise. Les cas UX-02 et UX-03 sont donc au verdict **NOT RUN** dans
> la matrice ; aucun résultat n'est affiché tant que les séances n'ont pas eu lieu. Après les séances : saisir les notes
> brutes (§ 6), calculer les indicateurs par script, compléter le tableau ci-dessous et les problèmes (§ 8).

| Indicateur | T1 | T2 | T3 | Global | Cible | Atteinte |
| --- | --- | --- | --- | --- | --- | --- |
| Taux de réussite | | | | | >= 80 % | |
| Temps médian (s) | | | | | — | |
| Score SUS moyen | — | — | — | | >= 68 | |

## 8. Problèmes relevés (après les séances)

| N° | Problème | Tâche | Participants concernés | Gravité | Correction | Vérification (E2E rejoué) |
| --- | --- | --- | --- | --- | --- | --- |
