/**
 * End-to-end journeys E2E-01 to E2E-05 (docs/cahier-de-test.md §4), on chromium, firefox and mobile (Pixel 7).
 * Expected values come from the rules: BR-04 (3 x 40.00 € = 120.00 €, 5 % = 6.00 €, total 114.00 €), BR-01, BR-05.
 */
import { expect, test } from '@playwright/test';
import {
  ADMIN, STAFF, apiGet, apiToken, createCategory, createProduct, euros, placeOrder, registerCustomer, setStatus, uiLogin, uid,
} from './helpers';

test('E2E-01 parcours client complet : recherche, fiche, panier, connexion, commande @FR-01 @FR-06 @FR-10 @BR-04', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const category = await createCategory(request, staff, `Cat ${id}`);
  const p1 = await createProduct(request, staff, { name: `Mug ${id}`, price_cents: 4000, stock: 10, category_id: category });
  const ana = await registerCustomer(request, info);

  await page.goto('/');
  await page.getByRole('searchbox', { name: 'Rechercher' }).fill(id);
  await page.getByRole('link', { name: p1.name }).click();
  await expect(page.getByRole('heading', { level: 1, name: p1.name })).toBeVisible();
  await page.getByLabel('Quantité').fill('3');
  await page.getByRole('button', { name: 'Ajouter au panier' }).click();
  await page.getByRole('link', { name: 'Voir le panier' }).click();
  await page.getByRole('button', { name: 'Se connecter pour commander' }).click();
  await uiLogin(page, ana.email, ana.password);
  await expect(page).toHaveURL(/\/panier$/);
  await page.getByRole('button', { name: 'Commander' }).click();

  await expect(page).toHaveURL(/\/commandes$/);
  await expect(page.getByRole('status')).toContainText('enregistrée');
  const row = page.getByRole('row').filter({ hasText: p1.name });
  await expect(row).toContainText('Passée');
  await expect(row).toContainText(euros(11400)); // total after the 5 % discount
  await expect(row).toContainText(euros(600)); // discount
});

test('E2E-02 refus pour rupture de stock @BR-01', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const category = await createCategory(request, staff, `Cat ${id}`);
  const p2 = await createProduct(request, staff, { name: `Lampe ${id}`, price_cents: 5000, stock: 3, category_id: category });
  const ana = await registerCustomer(request, info);

  await uiLogin(page, ana.email, ana.password);
  await page.goto(`/produits/${p2.id}`);
  await page.getByLabel('Quantité').fill('4');
  await page.getByRole('button', { name: 'Ajouter au panier' }).click();
  await page.goto('/panier');
  await page.getByRole('button', { name: 'Commander' }).click();

  await expect(page.getByRole('alert')).toContainText(`Stock insuffisant pour : ${p2.name}`);
  await expect(page).toHaveURL(/\/panier$/);
  expect(await apiGet<unknown[]>(request, ana.token, '/orders')).toHaveLength(0); // no order was added
  expect((await apiGet<{ stock: number }>(request, ana.token, `/products/${p2.id}`)).stock).toBe(3);
});

test('E2E-03 le personnel fait avancer une commande, seules les transitions permises sont proposées @FR-07 @BR-05', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const category = await createCategory(request, staff, `Cat ${id}`);
  const p = await createProduct(request, staff, { name: `Stylo ${id}`, price_cents: 1000, stock: 10, category_id: category });
  const ana = await registerCustomer(request, info);
  const order = await placeOrder(request, ana.token, [{ product_id: p.id, quantity: 1 }]);

  await uiLogin(page, STAFF.email, STAFF.password);
  await page.getByRole('link', { name: 'Commandes', exact: true }).click();
  const row = page.locator(`tr[data-order-id="${order.id}"]`);
  const buttons = row.getByRole('button');

  await expect(row.getByTestId('status')).toHaveText('Passée');
  await expect(buttons).toHaveText(['Marquer payée', 'Annuler']);
  await row.getByRole('button', { name: /Marquer payée/ }).click();

  await expect(row.getByTestId('status')).toHaveText('Payée');
  await expect(buttons).toHaveText(['Marquer expédiée', 'Annuler']);
  await row.getByRole('button', { name: /Marquer expédiée/ }).click();

  await expect(row.getByTestId('status')).toHaveText('Expédiée');
  await expect(buttons).toHaveText(['Marquer livrée']); // cancelling is no longer offered (BR-06)
  const fromApi = await apiGet<{ status: string }>(request, staff, `/orders/${order.id}`);
  expect(fromApi.status).toBe('SHIPPED');
});

test('E2E-04 créer puis supprimer un produit avec confirmation, erreur affichée sous le champ @FR-04 @QR-US-02', async ({ page, request }, info) => {
  const admin = await apiToken(request, ADMIN.email, ADMIN.password);
  const id = uid(info);
  await createCategory(request, admin, `Cat ${id}`);
  const name = `Agenda ${id}`;

  await uiLogin(page, ADMIN.email, ADMIN.password);
  await page.getByRole('link', { name: 'Produits', exact: true }).click();
  const form = page.getByRole('form', { name: 'Nouveau produit' });
  await form.getByLabel('Référence (SKU)').fill(`AG-${id}`);
  await form.getByLabel('Nom').fill(name);
  await form.getByLabel('Prix (€)').fill('-5');
  await form.getByLabel('Stock').fill('7');
  await form.getByLabel('Catégorie').selectOption({ label: `Cat ${id}` });
  await form.getByRole('button', { name: 'Créer le produit' }).click();

  const price = form.getByLabel('Prix (€)');
  await expect(price).toHaveAttribute('aria-invalid', 'true');
  await expect(form.getByText('La valeur doit être supérieure ou égale à 0.')).toBeVisible(); // under the field
  await price.fill('12,50');
  await form.getByRole('button', { name: 'Créer le produit' }).click();
  await expect(page.getByRole('status')).toContainText(`« ${name} » créé`);
  type Found = { total: number; items: { id: number; price_cents: number; stock: number }[] };
  const inApi = () => apiGet<Found>(request, admin, `/products?q=${encodeURIComponent(id)}`);
  const created = await inApi();
  expect(created.total).toBe(1); // really created, with the values typed in the form
  expect(created.items[0]).toMatchObject({ price_cents: 1250, stock: 7 });

  await page.getByRole('searchbox', { name: 'Filtrer' }).fill(id);
  const row = page.getByRole('row').filter({ hasText: name });
  await row.getByRole('button', { name: `Supprimer ${name}` }).click();
  const dialog = page.getByRole('dialog', { name: 'Supprimer le produit ?' });
  await expect(dialog).toBeVisible();
  await dialog.getByRole('button', { name: 'Annuler' }).click();
  await expect(dialog).toBeHidden();
  await expect(row).toBeVisible(); // still there after "Annuler"…
  expect((await inApi()).total).toBe(1); // …and still in the API: the dialog protected it

  await row.getByRole('button', { name: `Supprimer ${name}` }).click();
  await dialog.getByRole('button', { name: 'Supprimer définitivement' }).click();
  await expect(row).toHaveCount(0);
  expect((await inApi()).total).toBe(0); // gone in the API too
});

test('E2E-05 filtres du tableau de bord : mêmes indicateurs que l’API @FR-09', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const catName = `Cat ${id}`;
  const category = await createCategory(request, staff, catName);
  const p = await createProduct(request, staff, { name: `Bol ${id}`, price_cents: 4000, stock: 20, category_id: category });
  const ana = await registerCustomer(request, info);
  const paid = await placeOrder(request, ana.token, [{ product_id: p.id, quantity: 3 }]);
  await placeOrder(request, ana.token, [{ product_id: p.id, quantity: 1 }]);
  await setStatus(request, staff, paid.id, 'PAID');
  const today = (await apiGet<{ created_at: string }>(request, staff, `/orders/${paid.id}`)).created_at.slice(0, 10); // UTC day
  const api = await apiGet<{ revenue_cents: number; orders_by_status: Record<string, number> }>(
    request, staff, `/dashboard?date_from=${today}&date_to=${today}&category_id=${category}`,
  );
  expect(api.revenue_cents).toBe(11400); // from BR-04 and decision Q-03: only the PAID order counts
  expect(api.orders_by_status.PLACED).toBe(1);
  expect(api.orders_by_status.PAID).toBe(1);

  await uiLogin(page, STAFF.email, STAFF.password);
  await page.getByRole('link', { name: 'Tableau de bord' }).click();
  await page.getByRole('textbox', { name: 'Du', exact: true }).fill(today);
  await page.getByRole('textbox', { name: 'Au', exact: true }).fill(today);
  await page.getByRole('combobox', { name: 'Catégorie' }).selectOption({ label: catName });

  await expect(page.getByTestId('revenue')).toHaveText(euros(api.revenue_cents));
  await expect(page.getByTestId('count-PAID')).toHaveText(String(api.orders_by_status.PAID));
  await expect(page.getByTestId('count-PLACED')).toHaveText(String(api.orders_by_status.PLACED));
  await expect(page.getByTestId('top-products')).toContainText(`Bol ${id} — 3`);

  // A past period excludes today's orders: the period filter really applies (Q-04).
  await page.getByRole('textbox', { name: 'Du', exact: true }).fill('2020-01-01');
  await page.getByRole('textbox', { name: 'Au', exact: true }).fill('2020-01-31');
  await expect(page.getByTestId('revenue')).toHaveText(euros(0));
  await expect(page.getByTestId('count-PAID')).toHaveText('0');
  // Start after end is refused with a clear message (Q-04: 422).
  await page.getByRole('textbox', { name: 'Du', exact: true }).fill(today);
  await expect(page.getByRole('alert')).toContainText('la date de début doit précéder la date de fin');
});
