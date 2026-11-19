# Couverture de l'API (route × méthode × code)

Généré par `tools/api_coverage.py` le 2026-11-19T22:50:56+00:00 à partir de `reports/junit-api.xml`, `reports/junit-integration.xml` et du contrat OpenAPI de l'application.

- Opérations exercées : 25 / 25
- Codes documentés obtenus (hors 422 automatique non obtenu) : 74 / 95
- Appels HTTP enregistrés : 212

| Méthode | Route | Codes documentés : obtenu ? | Codes obtenus non documentés |
| --- | --- | --- | --- |
| `GET` | `/api/audit` | 200 oui, 401 oui, 403 oui, 422 oui | — |
| `GET` | `/api/audit/{entry_id}` | 200 oui, 401 oui, 403 oui, 404 non, 422 non | — |
| `POST` | `/api/auth/login` | 200 oui, 400 non, 401 oui, 422 oui | — |
| `GET` | `/api/auth/me` | 200 oui, 401 oui | — |
| `POST` | `/api/auth/register` | 201 oui, 400 non, 409 oui, 422 oui | — |
| `GET` | `/api/categories` | 200 oui | — |
| `POST` | `/api/categories` | 201 oui, 400 non, 401 oui, 403 oui, 409 oui, 422 oui | — |
| `DELETE` | `/api/categories/{category_id}` | 204 oui, 401 oui, 403 oui, 404 non, 409 oui, 422 non | — |
| `GET` | `/api/categories/{category_id}` | 200 oui, 404 oui, 422 non | — |
| `PUT` | `/api/categories/{category_id}` | 200 oui, 400 non, 401 oui, 403 oui, 404 non, 409 non, 422 non | — |
| `GET` | `/api/dashboard` | 200 oui, 401 oui, 403 oui, 422 oui | — |
| `GET` | `/api/health` | 200 oui, 503 non | — |
| `GET` | `/api/orders` | 200 oui, 401 oui | — |
| `POST` | `/api/orders` | 201 oui, 400 non, 401 oui, 403 oui, 404 oui, 409 oui, 422 oui | — |
| `GET` | `/api/orders/{order_id}` | 200 oui, 401 oui, 404 oui, 422 oui | — |
| `POST` | `/api/orders/{order_id}/cancel` | 200 oui, 401 oui, 403 oui, 404 oui, 409 oui, 422 non | — |
| `PATCH` | `/api/orders/{order_id}/status` | 200 oui, 400 non, 401 oui, 403 oui, 404 non, 409 oui, 422 non | — |
| `GET` | `/api/products` | 200 oui, 422 oui | — |
| `POST` | `/api/products` | 201 oui, 400 non, 401 oui, 403 oui, 404 non, 409 oui, 422 oui | — |
| `DELETE` | `/api/products/{product_id}` | 204 oui, 401 oui, 403 oui, 404 non, 409 oui, 422 non | — |
| `GET` | `/api/products/{product_id}` | 200 oui, 404 oui, 422 oui | — |
| `PUT` | `/api/products/{product_id}` | 200 oui, 400 non, 401 oui, 403 oui, 404 non, 409 non, 422 non | — |
| `GET` | `/api/users` | 200 oui, 401 oui, 403 oui | — |
| `PATCH` | `/api/users/{user_id}/deactivate` | 200 oui, 401 oui, 403 oui, 404 non, 409 oui, 422 non | — |
| `PATCH` | `/api/users/{user_id}/role` | 200 oui, 400 non, 401 oui, 403 oui, 404 non, 409 oui, 422 non | — |

Appels vers une route absente du contrat : DELETE /api/audit/{entry_id}, PATCH /api/audit/{entry_id}, PATCH /api/categories, PATCH /api/products/{product_id}, PUT /api/audit/{entry_id}
