# Matrice de traçabilité (générée)

Générée par `tools/trace.py` le 2026-11-20T00:23:08+00:00, commit `99a818c`, à partir de `docs/exigences.yaml` et des rapports bruts de `reports/`. Ne pas modifier à la main : relancer `/trace`.

## Synthèse par exigence

| Verdict | Nombre |
| --- | --- |
| PASS | 34 |
| PARTIAL | 2 |

| Exigence | Type | Priorité | Caractéristique | Verdict |
| --- | --- | --- | --- | --- |
| FR-01 | FR | P0 | securite | PASS |
| FR-02 | FR | P0 | securite | PASS |
| FR-03 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-04 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-05 | FR | P1 | securite | PASS |
| FR-06 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-07 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-08 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-09 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-10 | FR | P0 | aptitude_fonctionnelle | PASS |
| FR-11 | FR | P0 | securite | PASS |
| BR-01 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-02 | BR | P0 | securite | PASS |
| BR-03 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-04 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-05 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-06 | BR | P0 | fiabilite | PASS |
| BR-07 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-08 | BR | P0 | securite | PASS |
| BR-09 | BR | P0 | aptitude_fonctionnelle | PASS |
| BR-10 | BR | P1 | aptitude_fonctionnelle | PASS |
| BR-11 | BR | P1 | securite | PASS |
| QR-FS-01 | QR | P0 | aptitude_fonctionnelle | PASS |
| QR-PE-01 | QR | P0 | efficacite_performance | PASS |
| QR-PE-02 | QR | P0 | efficacite_performance | PASS |
| QR-CO-01 | QR | P0 | compatibilite | PASS |
| QR-CO-02 | QR | P0 | compatibilite | PASS |
| QR-US-01 | QR | P0 | utilisabilite | PASS |
| QR-US-02 | QR | P1 | utilisabilite | PARTIAL |
| QR-RE-01 | QR | P0 | fiabilite | PASS |
| QR-RE-02 | QR | P0 | fiabilite | PASS |
| QR-SE-01 | QR | P0 | securite | PASS |
| QR-SE-02 | QR | P0 | securite | PASS |
| QR-MA-01 | QR | P0 | maintenabilite | PASS |
| QR-MA-02 | QR | P0 | maintenabilite | PASS |
| QR-PO-01 | QR | P0 | portabilite | PARTIAL |

## Détail : exigence → condition → scénario → cas → script → outil → verdict → preuve

| exigence | condition de test | scénario | cas de test | script | outil | verdict | mesure | preuve | commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FR-01 | Inscription d'un client | SC-FR-01-1, SC-FR-01-2 | TA-01 | tests.api.test_accounts_admin_api::test_register_then_login[TA-01] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-01 | Mauvais mot de passe | SC-FR-01-1, SC-FR-01-2 | TA-02 | tests.api.test_accounts_admin_api::test_wrong_password[TA-02] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-01 | Commande sans jeton (R1) | SC-FR-01-1, SC-FR-01-2 | TA-03 | tests.api.test_orders_api::test_r1_no_token[TA-03] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-01 | Un jeton valide identifie l'utilisateur et son rôle | SC-FR-01-1, SC-FR-01-2 | IT-01 | tests.integration.test_interfaces::test_valid_token_identifies_user_and_role[IT-01] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-01 | Un jeton expiré ou falsifié est refusé | SC-FR-01-1, SC-FR-01-2 | IT-02 | tests.integration.test_interfaces::test_expired_or_forged_token_is_refused[IT-02-expired] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-01 | Session : jeton expiré, jeton émis avant un changement de rôle | SC-FR-01-1, SC-FR-01-2 | SEC-04 | tests.security.test_attacks::test_expired_session_requires_new_login[SEC-04-expired] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-security.xml | 99a818c |
| FR-01 | Parcours client complet | SC-FR-01-1, SC-FR-01-2 | E2E-01 | parcours.spec.ts::E2E-01 parcours client complet : recherche, fiche, panier, connexion, commande @FR-01 @FR-06 @FR-10 @BR-04 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| FR-02 | Matrice des droits complète | SC-FR-02-1, SC-FR-02-2 | TA-20 | tests.api.test_rbac::test_permissions_matrix[TA-20 ANONYMOUS GET /api/health] (+107) | pytest | PASS | 108/108 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-02 | Contrôle d'accès par numéro de commande | SC-FR-02-1, SC-FR-02-2 | SEC-03 | tests.security.test_attacks::test_access_control_with_another_customers_order_id[SEC-03-read] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-security.xml | 99a818c |
| FR-03 | Cycle de vie d'une catégorie | SC-FR-03-1, SC-FR-03-2 | TA-08 | tests.api.test_catalog_api::test_category_lifecycle[TA-08] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-04 | Cycle de vie d'un produit | SC-FR-04-1, SC-FR-04-2 | TA-09 | tests.api.test_catalog_api::test_product_lifecycle[TA-09] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-04 | Créer puis supprimer un produit avec confirmation | SC-FR-04-1, SC-FR-04-2 | E2E-04 | parcours.spec.ts::E2E-04 créer puis supprimer un produit avec confirmation, erreur affichée sous le champ @FR-04 @QR-US-02 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| FR-05 | Changement de rôle par l'ADMIN | SC-FR-05-1, SC-FR-05-2 | TA-21 | tests.api.test_accounts_admin_api::test_admin_changes_roles[TA-21] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-05 | Compte désactivé | SC-FR-05-1, SC-FR-05-2 | TA-22 | tests.api.test_accounts_admin_api::test_deactivated_account[TA-22] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Commande sans jeton (R1) | SC-FR-06-1, SC-FR-06-2 | TA-03 | tests.api.test_orders_api::test_r1_no_token[TA-03] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Commande valide avec remise (R5) | SC-FR-06-1, SC-FR-06-2 | TA-04 | tests.api.test_orders_api::test_r5_valid_order_with_discount[TA-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Corps invalide (R2) | SC-FR-06-1, SC-FR-06-2 | TA-05 | tests.api.test_orders_api::test_r2_invalid_body[TA-05-quantity] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Stock insuffisant (R4) | SC-FR-06-1, SC-FR-06-2 | TA-06 | tests.api.test_orders_api::test_r4_out_of_stock[TA-06] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Prix client ignoré | SC-FR-06-1, SC-FR-06-2 | TA-07 | tests.api.test_orders_api::test_client_price_is_ignored[TA-07] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Annulation par le client | SC-FR-06-1, SC-FR-06-2 | TA-14 | tests.api.test_orders_api::test_customer_cancels_own_order[TA-14] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Produit inexistant (R3) | SC-FR-06-1, SC-FR-06-2 | TA-29 | tests.api.test_orders_api::test_r3_unknown_product[TA-29] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-06 | Parcours client complet | SC-FR-06-1, SC-FR-06-2 | E2E-01 | parcours.spec.ts::E2E-01 parcours client complet : recherche, fiche, panier, connexion, commande @FR-01 @FR-06 @FR-10 @BR-04 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| FR-07 | Workflow par le personnel | SC-FR-07-1, SC-FR-07-2 | TA-15 | tests.api.test_orders_api::test_staff_moves_order_through_workflow[TA-15] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-07 | Transition interdite par l'API | SC-FR-07-1, SC-FR-07-2 | TA-16 | tests.api.test_orders_api::test_forbidden_transition_through_api[TA-16] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-07 | Liste des commandes paginée et filtrée | SC-FR-07-1, SC-FR-07-2 | TA-38 | tests.api.test_orders_api::test_back_office_order_list_is_paginated_and_filtered[TA-38] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-07 | Le personnel fait avancer une commande | SC-FR-07-1, SC-FR-07-2 | E2E-03 | parcours.spec.ts::E2E-03 le personnel fait avancer une commande, seules les transitions permises sont proposées @FR-07 @BR-05 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| FR-08 | Payer une commande PLACED | SC-FR-08-1 | CT-19 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-19] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-08 | Expédier une commande PAID | SC-FR-08-1 | CT-20 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-20] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-08 | Livrer une commande SHIPPED | SC-FR-08-1 | CT-21 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-21] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-08 | Annuler une commande PLACED | SC-FR-08-1 | CT-22 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-22] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-08 | Annuler une commande PAID | SC-FR-08-1 | CT-23 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-23] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-08 | L'annulation remet le stock en base | SC-FR-08-1 | IT-07 | tests.integration.test_interfaces::test_cancel_restocks_in_database[IT-07] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-09 | Seuil du stock faible | SC-FR-09-1, SC-FR-09-2 | CT-48 | tests.unit.test_dashboard_rules::test_low_stock_threshold[CT-48] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-09 | Top 5 des produits vendus | SC-FR-09-1, SC-FR-09-2 | CT-49 | tests.unit.test_dashboard_rules::test_top_five_products[CT-49] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-09 | Statuts comptés dans le chiffre d'affaires | SC-FR-09-1, SC-FR-09-2 | CT-50 | tests.unit.test_dashboard_rules::test_revenue_counts_paid_shipped_delivered[CT-50] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| FR-09 | Indicateurs du tableau de bord sur un jeu maîtrisé | SC-FR-09-1, SC-FR-09-2 | IT-11 | tests.integration.test_interfaces::test_dashboard_indicators_on_controlled_data[IT-11] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-09 | Filtres période et catégorie ; période invalide | SC-FR-09-1, SC-FR-09-2 | IT-12 | tests.integration.test_interfaces::test_dashboard_period_and_category_filters[IT-12] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-09 | Tableau de bord : droits et filtres | SC-FR-09-1, SC-FR-09-2 | TA-17 | tests.api.test_accounts_admin_api::test_dashboard_rights_and_values[TA-17] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-09 | Filtres du tableau de bord | SC-FR-09-1, SC-FR-09-2 | E2E-05 | parcours.spec.ts::E2E-05 filtres du tableau de bord : mêmes indicateurs que l’API @FR-09 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| FR-10 | Filtres de recherche combinés | SC-FR-10-1, SC-FR-10-2 | IT-13 | tests.integration.test_interfaces::test_combined_search_filters[IT-13] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-10 | Paramètres de recherche invalides | SC-FR-10-1, SC-FR-10-2 | IT-14 | tests.integration.test_interfaces::test_invalid_search_parameters[IT-14-limit0] (+2) | pytest | PASS | 3/3 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-10 | Recherche filtrée sur 50 000 produits | SC-FR-10-1, SC-FR-10-2 | TA-18 | tests.api.test_catalog_api::test_filtered_search_on_50000_products[TA-18] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-10 | Paramètres de recherche invalides | SC-FR-10-1, SC-FR-10-2 | TA-19 | tests.api.test_catalog_api::test_invalid_search_parameters_never_500[TA-19-limit0] (+2) | pytest | PASS | 3/3 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-10 | Injection SQL dans la recherche | SC-FR-10-1, SC-FR-10-2 | SEC-01 | tests.security.test_attacks::test_sql_injection_in_search_is_plain_text[SEC-01-or-true] (+3) | pytest | PASS | 4/4 exécutions réussies | reports/junit-security.xml | 99a818c |
| FR-10 | Recherche filtrée sur 50 000 produits | SC-FR-10-1, SC-FR-10-2 | PERF-03 | k6 | k6 | PASS | k6 : p95{name:search} = 64 ms; p95 = 64 ms; erreurs = 0.00 % | reports/perf/search.json | 99a818c |
| FR-11 | L'action et son audit sont écrits ensemble | SC-FR-11-1, SC-FR-11-2 | IT-09 | tests.integration.test_interfaces::test_action_and_audit_are_written_together[IT-09] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-11 | Action échouée = aucune entrée d'audit | SC-FR-11-1, SC-FR-11-2 | IT-10 | tests.integration.test_interfaces::test_failed_action_leaves_no_audit_entry[IT-10] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| FR-11 | Mauvais mot de passe | SC-FR-11-1, SC-FR-11-2 | TA-02 | tests.api.test_accounts_admin_api::test_wrong_password[TA-02] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-11 | Workflow par le personnel | SC-FR-11-1, SC-FR-11-2 | TA-15 | tests.api.test_orders_api::test_staff_moves_order_through_workflow[TA-15] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-11 | Changement de rôle par l'ADMIN | SC-FR-11-1, SC-FR-11-2 | TA-21 | tests.api.test_accounts_admin_api::test_admin_changes_roles[TA-21] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-11 | Journal d'audit non modifiable | SC-FR-11-1, SC-FR-11-2 | TA-23 | tests.api.test_accounts_admin_api::test_audit_log_cannot_be_changed[TA-23-put] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-11 | Lecture du journal d'audit | SC-FR-11-1, SC-FR-11-2 | TA-24 | tests.api.test_accounts_admin_api::test_audit_log_reading_rights[TA-24] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| FR-11 | Annulation et modifications de produit journalisées | SC-FR-11-1, SC-FR-11-2 | TA-37 | tests.api.test_orders_api::test_cancel_and_product_changes_are_audited[TA-37] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-01 | Quantité égale au stock acceptée | SC-BR-01-1, SC-BR-01-2 | CT-44 | tests.unit.test_order_rules::test_quantity_equal_to_stock_is_accepted[CT-44] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-01 | Quantité au-delà du stock refusée | SC-BR-01-1, SC-BR-01-2 | CT-45 | tests.unit.test_order_rules::test_quantity_above_stock_refuses_the_whole_order[CT-45] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-01 | Une seule ligne en rupture bloque tout | SC-BR-01-1, SC-BR-01-2 | CT-46 | tests.unit.test_order_rules::test_quantity_above_stock_refuses_the_whole_order[CT-46] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-01 | La commande décrémente le stock en base | SC-BR-01-1, SC-BR-01-2 | IT-03 | tests.integration.test_interfaces::test_order_decrements_stock_in_database[IT-03] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-01 | Une panne à la 2e écriture n'écrit rien | SC-BR-01-1, SC-BR-01-2 | IT-04 | tests.integration.test_interfaces::test_failure_on_second_write_writes_nothing[IT-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-01 | Commande valide avec remise (R5) | SC-BR-01-1, SC-BR-01-2 | TA-04 | tests.api.test_orders_api::test_r5_valid_order_with_discount[TA-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-01 | Stock insuffisant (R4) | SC-BR-01-1, SC-BR-01-2 | TA-06 | tests.api.test_orders_api::test_r4_out_of_stock[TA-06] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-01 | Deux commandes simultanées, dernières unités | SC-BR-01-1, SC-BR-01-2 | TA-13 | tests.api.test_orders_api::test_two_simultaneous_orders_for_the_last_units[TA-13] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-01 | Refus pour rupture de stock | SC-BR-01-1, SC-BR-01-2 | E2E-02 | parcours.spec.ts::E2E-02 refus pour rupture de stock @BR-01 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| BR-01 | Double soumission simultanée | SC-BR-01-1, SC-BR-01-2 | REL-04 | tests.reliability.test_reliability::test_same_order_submitted_twice_at_once_never_oversells[REL-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-reliability.xml | 99a818c |
| BR-02 | Le prix client est ignoré | SC-BR-02-1, SC-BR-02-2 | CT-47 | tests.unit.test_order_rules::test_client_price_is_ignored[CT-47] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-02 | Le prix vient du catalogue en base | SC-BR-02-1, SC-BR-02-2 | IT-05 | tests.integration.test_interfaces::test_price_comes_from_catalogue_and_is_frozen[IT-05] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-02 | Prix client ignoré | SC-BR-02-1, SC-BR-02-2 | TA-07 | tests.api.test_orders_api::test_client_price_is_ignored[TA-07] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-03 | Refuser une quantité nulle | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-01 | tests.unit.test_order_rules::test_invalid_order_shape_is_refused[CT-01] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Accepter la quantité minimale | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-02 | tests.unit.test_order_rules::test_valid_order_shape_is_accepted[CT-02] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Accepter la quantité maximale | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-03 | tests.unit.test_order_rules::test_valid_order_shape_is_accepted[CT-03] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Refuser la quantité au-delà du maximum | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-04 | tests.unit.test_order_rules::test_invalid_order_shape_is_refused[CT-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Refuser une quantité négative | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-05 | tests.unit.test_order_rules::test_invalid_order_shape_is_refused[CT-05] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Refuser une commande vide | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-06 | tests.unit.test_order_rules::test_invalid_order_shape_is_refused[CT-06] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Accepter une seule ligne | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-07 | tests.unit.test_order_rules::test_valid_order_shape_is_accepted[CT-07] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Accepter 50 lignes | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-08 | tests.unit.test_order_rules::test_valid_order_shape_is_accepted[CT-08] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Refuser 51 lignes | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-09 | tests.unit.test_order_rules::test_invalid_order_shape_is_refused[CT-09] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Bornes contrôlées avant la fusion des doublons | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | CT-51 | tests.unit.test_order_rules::test_bounds_apply_to_lines_as_sent_then_lines_merge[CT-51] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-03 | Corps invalide (R2) | SC-BR-03-1, SC-BR-03-2, SC-BR-03-3 | TA-05 | tests.api.test_orders_api::test_r2_invalid_body[TA-05-quantity] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-04 | Pas de remise, partition basse | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-10 | tests.unit.test_pricing::test_discount[CT-10] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | Pas de remise, juste sous 100 € | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-11 | tests.unit.test_pricing::test_discount[CT-11] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | 5 % à la limite basse | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-12 | tests.unit.test_pricing::test_discount[CT-12] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | 5 %, représentant | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-13 | tests.unit.test_pricing::test_discount[CT-13] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | 5 % juste sous 200 €, avec arrondi | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-14 | tests.unit.test_pricing::test_discount[CT-14] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | 10 % à la limite | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-15 | tests.unit.test_pricing::test_discount[CT-15] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | 10 %, représentant | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-16 | tests.unit.test_pricing::test_discount[CT-16] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | Arrondi demi vers le haut | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-17 | tests.unit.test_pricing::test_discount[CT-17] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | Refuser un sous-total négatif | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-18 | tests.unit.test_pricing::test_negative_subtotal_is_refused[CT-18] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | Pas de remise, limite basse | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | CT-52 | tests.unit.test_pricing::test_discount[CT-52] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-04 | Flux de données sous-total → remise → total → stock → lignes | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | IT-06 | tests.integration.test_interfaces::test_data_flow_subtotal_discount_total_stock_rows[IT-06] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-04 | Commande valide avec remise (R5) | SC-BR-04-1, SC-BR-04-2, SC-BR-04-3, SC-BR-04-4, SC-BR-04-5 | TA-04 | tests.api.test_orders_api::test_r5_valid_order_with_discount[TA-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-05 | Payer une commande PLACED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-19 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-19] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Expédier une commande PAID | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-20 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-20] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Livrer une commande SHIPPED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-21 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-21] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Annuler une commande PLACED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-22 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-22] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Annuler une commande PAID | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-23 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-23] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Expédier sans paiement | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-24 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-24] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Livrer depuis PLACED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-25 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-25] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Payer deux fois | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-26 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-26] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Livrer depuis PAID | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-27 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-27] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Payer une commande expédiée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-28 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-28] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Expédier deux fois | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-29 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-29] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Annuler après expédition | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-30 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-30] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Payer une commande livrée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-31 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-31] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Expédier une commande livrée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-32 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-32] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Livrer deux fois | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-33 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-33] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Annuler une commande livrée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-34 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-34] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Payer une commande annulée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-35 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-35] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Expédier une commande annulée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-36 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-36] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Livrer une commande annulée | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-37 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-37] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Annuler deux fois | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-38 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-38] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Un client ne peut pas payer | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-39 | tests.unit.test_workflow::test_customer_may_not_apply[CT-39] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Un client annule sa commande PLACED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-40 | tests.unit.test_workflow::test_customer_cancels_own_placed_order[CT-40] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Un client annule sa commande PAID | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-41 | tests.unit.test_workflow::test_customer_may_not_apply[CT-41] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | L'ADMIN a les mêmes droits que STAFF | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-53 | tests.unit.test_workflow::test_admin_has_the_same_rights_as_staff[CT-53] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Un client ne peut pas expédier | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-54 | tests.unit.test_workflow::test_customer_may_not_apply[CT-54] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Un client ne peut pas livrer | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | CT-55 | tests.unit.test_workflow::test_customer_may_not_apply[CT-55] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-05 | Workflow par le personnel | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | TA-15 | tests.api.test_orders_api::test_staff_moves_order_through_workflow[TA-15] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-05 | Transition interdite par l'API | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | TA-16 | tests.api.test_orders_api::test_forbidden_transition_through_api[TA-16] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-05 | Un client n'annule ni une commande PAID ni une commande SHIPPED | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | TA-36 | tests.api.test_orders_api::test_customer_cannot_cancel_paid_or_shipped_order[TA-36-paid] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-05 | Le personnel fait avancer une commande | SC-BR-05-1, SC-BR-05-2, SC-BR-05-3 | E2E-03 | parcours.spec.ts::E2E-03 le personnel fait avancer une commande, seules les transitions permises sont proposées @FR-07 @BR-05 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| BR-06 | Annuler une commande PLACED | SC-BR-06-1, SC-BR-06-2 | CT-22 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-22] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | Annuler une commande PAID | SC-BR-06-1, SC-BR-06-2 | CT-23 | tests.unit.test_workflow::test_allowed_transition_by_staff[CT-23] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | Annuler après expédition | SC-BR-06-1, SC-BR-06-2 | CT-30 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-30] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | Annuler une commande livrée | SC-BR-06-1, SC-BR-06-2 | CT-34 | tests.unit.test_workflow::test_forbidden_transition_is_refused[CT-34] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | L'annulation remet chaque ligne en stock | SC-BR-06-1, SC-BR-06-2 | CT-42 | tests.unit.test_workflow::test_cancel_puts_every_line_back_in_stock[CT-42] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | Pas de remise en stock après expédition | SC-BR-06-1, SC-BR-06-2 | CT-43 | tests.unit.test_workflow::test_no_restock_after_shipping[CT-43] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | Un client n'annule pas une commande expédiée | SC-BR-06-1, SC-BR-06-2 | CT-56 | tests.unit.test_workflow::test_no_restock_after_shipping[CT-56] | pytest | PASS | 1/1 exécutions réussies | reports/junit-unit.xml | 99a818c |
| BR-06 | L'annulation remet le stock en base | SC-BR-06-1, SC-BR-06-2 | IT-07 | tests.integration.test_interfaces::test_cancel_restocks_in_database[IT-07] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-06 | Annulation refusée après expédition, base inchangée | SC-BR-06-1, SC-BR-06-2 | IT-08 | tests.integration.test_interfaces::test_cancel_after_shipping_leaves_database_unchanged[IT-08] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| BR-06 | Annulation par le client | SC-BR-06-1, SC-BR-06-2 | TA-14 | tests.api.test_orders_api::test_customer_cancels_own_order[TA-14] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-06 | Transition interdite par l'API | SC-BR-06-1, SC-BR-06-2 | TA-16 | tests.api.test_orders_api::test_forbidden_transition_through_api[TA-16] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-06 | Un client n'annule ni une commande PAID ni une commande SHIPPED | SC-BR-06-1, SC-BR-06-2 | TA-36 | tests.api.test_orders_api::test_customer_cannot_cancel_paid_or_shipped_order[TA-36-paid] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-07 | Email déjà pris, autre casse | SC-BR-07-1, SC-BR-07-2 | TA-10 | tests.api.test_accounts_admin_api::test_duplicate_email_other_case[TA-10] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-07 | SKU déjà pris | SC-BR-07-1, SC-BR-07-2 | TA-11 | tests.api.test_catalog_api::test_duplicate_sku_any_case[TA-11] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-07 | Nom de catégorie déjà pris | SC-BR-07-1, SC-BR-07-2 | TA-12 | tests.api.test_catalog_api::test_duplicate_category_name_any_case[TA-12] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-08 | Un client ne lit pas la commande d'un autre | SC-BR-08-1, SC-BR-08-2 | TA-25 | tests.api.test_orders_api::test_customer_cannot_read_another_customers_order[TA-25] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-08 | Un client n'annule pas la commande d'un autre | SC-BR-08-1, SC-BR-08-2 | TA-26 | tests.api.test_orders_api::test_customer_cannot_cancel_another_customers_order[TA-26] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-08 | Contrôle d'accès par numéro de commande | SC-BR-08-1, SC-BR-08-2 | SEC-03 | tests.security.test_attacks::test_access_control_with_another_customers_order_id[SEC-03-read] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-security.xml | 99a818c |
| BR-09 | Cycle de vie d'une catégorie | SC-BR-09-1, SC-BR-09-2 | TA-08 | tests.api.test_catalog_api::test_category_lifecycle[TA-08] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-09 | Suppression d'une catégorie non vide | SC-BR-09-1, SC-BR-09-2 | TA-27 | tests.api.test_catalog_api::test_delete_non_empty_category[TA-27] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-10 | Cycle de vie d'un produit | SC-BR-10-1, SC-BR-10-2 | TA-09 | tests.api.test_catalog_api::test_product_lifecycle[TA-09] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-10 | Suppression d'un produit déjà commandé | SC-BR-10-1, SC-BR-10-2 | TA-30 | tests.api.test_catalog_api::test_delete_product_already_ordered[TA-30] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-11 | Changement de rôle par l'ADMIN | SC-BR-11-1, SC-BR-11-2 | TA-21 | tests.api.test_accounts_admin_api::test_admin_changes_roles[TA-21] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| BR-11 | Le dernier ADMIN ne peut pas disparaître | SC-BR-11-1, SC-BR-11-2 | TA-31 | tests.api.test_accounts_admin_api::test_last_admin_cannot_disappear[TA-31] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-PE-01 | Smoke de performance |  | PERF-01 | k6 | k6 | PASS | k6 : p95 = 64 ms; erreurs = 0.00 % | reports/perf/smoke.json | 99a818c |
| QR-PE-01 | Charge sur liste et détail |  | PERF-02 | k6 | k6 | PASS | k6 : p95{name:list} = 77 ms; p95{name:detail} = 49 ms; p95 = 66 ms | reports/perf/load.json | 99a818c |
| QR-PE-02 | Recherche filtrée sur 50 000 produits |  | PERF-03 | k6 | k6 | PASS | k6 : p95{name:search} = 64 ms; p95 = 64 ms; erreurs = 0.00 % | reports/perf/search.json | 99a818c |
| QR-CO-01 | Parcours client complet |  | E2E-01 | parcours.spec.ts::E2E-01 parcours client complet : recherche, fiche, panier, connexion, commande @FR-01 @FR-06 @FR-10 @BR-04 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-CO-01 | Refus pour rupture de stock |  | E2E-02 | parcours.spec.ts::E2E-02 refus pour rupture de stock @BR-01 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-CO-01 | Le personnel fait avancer une commande |  | E2E-03 | parcours.spec.ts::E2E-03 le personnel fait avancer une commande, seules les transitions permises sont proposées @FR-07 @BR-05 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-CO-01 | Créer puis supprimer un produit avec confirmation |  | E2E-04 | parcours.spec.ts::E2E-04 créer puis supprimer un produit avec confirmation, erreur affichée sous le champ @FR-04 @QR-US-02 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-CO-01 | Filtres du tableau de bord |  | E2E-05 | parcours.spec.ts::E2E-05 filtres du tableau de bord : mêmes indicateurs que l’API @FR-09 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-CO-02 | Contrat OpenAPI et robustesse |  | TA-28 | tests.contract.test_openapi_contract::test_api_respects_its_contract[POST /api/auth/register] (+24) | pytest | PASS | 25/25 exécutions réussies | reports/junit-contract.xml | 99a818c |
| QR-CO-02 | Nombre hors plage : refus précis, jamais 500 |  | TA-32 | tests.api.test_robustness_api::test_out_of_range_numbers_are_422_not_500[TA-32-path-above-bigint] (+4) | pytest | PASS | 5/5 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-CO-02 | Caractère NUL : refus précis, jamais 500 |  | TA-33 | tests.api.test_robustness_api::test_nul_character_is_422_not_500[TA-33-login] (+2) | pytest | PASS | 3/3 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-CO-02 | Types JSON respectés |  | TA-34 | tests.api.test_robustness_api::test_json_integer_types[TA-34-bool] (+4) | pytest | PASS | 5/5 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-CO-02 | En-tête `Allow` complet sur 405 |  | TA-35 | tests.api.test_robustness_api::test_405_lists_every_allowed_method[TA-35-collection] (+2) | pytest | PASS | 3/3 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-US-01 | Accessibilité de base |  | UX-01 | accessibilite.spec.ts::UX-01 accessibilité : catalogue, fiche produit et panier, avec contenu @QR-US-01 (+3) | Playwright | PASS | 4/4 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-US-02 | Réussite et temps des tâches |  | UX-02 | protocole + script | protocole + script | NOT RUN | sessions d'utilisabilité en attente | docs/utilisabilite.md | 99a818c |
| QR-US-02 | Satisfaction (SUS) |  | UX-03 | questionnaire SUS + script | questionnaire SUS + script | NOT RUN | sessions d'utilisabilité en attente | docs/utilisabilite.md | 99a818c |
| QR-US-02 | Créer puis supprimer un produit avec confirmation |  | E2E-04 | parcours.spec.ts::E2E-04 créer puis supprimer un produit avec confirmation, erreur affichée sous le champ @FR-04 @QR-US-02 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-RE-01 | Redémarrage de la base sous charge |  | REL-01 | tools/reliability.py + k6-like probe | tools/reliability.py + k6-like probe | PASS | reprise 3.15 s ; 500 hors panne : 0 ; commandes 201 retrouvées : 1784/1784 | reports/reliability/rel-01.json | 99a818c |
| QR-RE-01 | Arrêt brutal du conteneur API |  | REL-02 | tools/reliability.py | tools/reliability.py | PASS | reprise 3.27 s ; 500 hors panne : 0 ; commandes 201 retrouvées : 1774/1774 | reports/reliability/rel-02.json | 99a818c |
| QR-RE-02 | Une panne à la 2e écriture n'écrit rien |  | IT-04 | tests.integration.test_interfaces::test_failure_on_second_write_writes_nothing[IT-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-integration.xml | 99a818c |
| QR-RE-02 | Deux commandes simultanées, dernières unités |  | TA-13 | tests.api.test_orders_api::test_two_simultaneous_orders_for_the_last_units[TA-13] | pytest | PASS | 1/1 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-RE-02 | Panne entre deux écritures |  | REL-03 | tests.reliability.test_reliability::test_database_failure_between_two_writes_rolls_everything_back[REL-03] | pytest | PASS | 1/1 exécutions réussies | reports/junit-reliability.xml | 99a818c |
| QR-RE-02 | Double soumission simultanée |  | REL-04 | tests.reliability.test_reliability::test_same_order_submitted_twice_at_once_never_oversells[REL-04] | pytest | PASS | 1/1 exécutions réussies | reports/junit-reliability.xml | 99a818c |
| QR-SE-01 | SAST et secrets |  | SEC-05 | Semgrep, Bandit, gitleaks | Semgrep, Bandit, gitleaks | PASS | Bandit 0, Semgrep 1 (1 justifié), gitleaks 0 | reports/sast/ | 99a818c |
| QR-SE-01 | SCA, SBOM et licences |  | SEC-06 | pip-audit, npm audit, Trivy, Syft | pip-audit, npm audit, Trivy, Syft | PASS | pip-audit 0 (31 paquets), npm 0, Trivy 0 (images + dépôt) | reports/sca/ | 99a818c |
| QR-SE-01 | DAST passif puis actif |  | SEC-07 | OWASP ZAP | OWASP ZAP | PASS | ZAP : 6 alertes, 0 High/Medium non justifiée | reports/dast/ | 99a818c |
| QR-SE-02 | Matrice des droits complète |  | TA-20 | tests.api.test_rbac::test_permissions_matrix[TA-20 ANONYMOUS GET /api/health] (+107) | pytest | PASS | 108/108 exécutions réussies | reports/junit-api.xml | 99a818c |
| QR-SE-02 | Injection SQL dans la recherche |  | SEC-01 | tests.security.test_attacks::test_sql_injection_in_search_is_plain_text[SEC-01-or-true] (+3) | pytest | PASS | 4/4 exécutions réussies | reports/junit-security.xml | 99a818c |
| QR-SE-02 | XSS stocké dans un nom de produit |  | SEC-02 | securite.spec.ts::SEC-02 XSS stocké dans un nom de produit : affiché comme texte, jamais exécuté @QR-SE-02 (+4) | Playwright | PASS | 5/5 exécutions réussies | reports/junit-e2e-docker.xml, reports/junit-e2e.xml | 99a818c |
| QR-SE-02 | Contrôle d'accès par numéro de commande |  | SEC-03 | tests.security.test_attacks::test_access_control_with_another_customers_order_id[SEC-03-read] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-security.xml | 99a818c |
| QR-SE-02 | Session : jeton expiré, jeton émis avant un changement de rôle |  | SEC-04 | tests.security.test_attacks::test_expired_session_requires_new_login[SEC-04-expired] (+1) | pytest | PASS | 2/2 exécutions réussies | reports/junit-security.xml | 99a818c |
| QR-MA-01 | Couverture des services |  | MA-01 | pytest-cov | pytest-cov | PASS | app/services : instructions 388/391, branches 96/96, total 99.4 % | reports/coverage.xml | 99a818c |
| QR-MA-01 | Qualité des tests : mutation et propriété |  | MA-02 | Hypothesis, mutmut | Hypothesis, mutmut | PASS | Hypothesis OK ; mutants tués 128/133 (96 %) | reports/maintenabilite/ | 99a818c |
| QR-MA-02 | Complexité cyclomatique |  | MA-03 | radon, xenon | radon, xenon | PASS | radon : 129 blocs, maximum 9 | reports/maintenabilite/radon-cc.json | 99a818c |
| QR-MA-02 | Dépendances entre couches |  | MA-04 | import-linter, ruff | import-linter, ruff | PASS | import-linter : Contracts: 2 kept, 0 broken | reports/maintenabilite/import-linter.txt | 99a818c |
| QR-PO-01 | Installation propre chronométrée |  | PORT-01 | scripts/installation-propre.sh | scripts/installation-propre.sh | PASS | installation en 27 s | reports/portabilite/installation-desktop-svtshjh.log | 99a818c |
| QR-PO-01 | Installation sur une seconde machine |  | PORT-02 | docs/installation.md (seconde machine) | docs/installation.md (seconde machine) | NOT RUN | journal d'installation absent (seconde machine : en attente) | reports/portabilite/ | 99a818c |
| QR-FS-01 | Toutes les FR/BR P0 au verdict PASS | — | — | tools/trace.py | matrice | PASS | 19/19 FR/BR P0 au PASS | docs/tracabilite/matrice.csv | 99a818c |
