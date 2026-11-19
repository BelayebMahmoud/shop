/**
 * UX-01 (QR-US-01): axe-core on the 5 main pages, with real content on them, plus two interaction states
 * (confirmation dialog open, form showing field errors). Fails on any serious or critical violation.
 * Desktop chromium only. The full axe result of each page is written to reports/a11y/ and attached.
 */
import AxeBuilder from '@axe-core/playwright';
import { expect, test, type Page, type TestInfo } from '@playwright/test';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { STAFF, apiToken, createCategory, createProduct, placeOrder, registerCustomer, uiLogin, uid } from './helpers';

const REPORT_DIR = resolve(dirname(fileURLToPath(import.meta.url)), '../../reports/a11y');
const TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'];

test.skip(({ browserName, isMobile }) => browserName !== 'chromium' || isMobile, 'axe runs once, on desktop chromium');

async function audit(page: Page, info: TestInfo, name: string) {
  await expect(page.getByText('Chargement…')).toHaveCount(0); // data rendered before auditing
  const results = await new AxeBuilder({ page }).withTags(TAGS).analyze();
  mkdirSync(REPORT_DIR, { recursive: true });
  writeFileSync(resolve(REPORT_DIR, `${name}.json`), JSON.stringify(results, null, 2));
  await info.attach(`axe-${name}.json`, { body: JSON.stringify(results, null, 2), contentType: 'application/json' });
  const blocking = results.violations.filter(v => v.impact === 'serious' || v.impact === 'critical');
  expect(blocking.map(v => `${v.id} (${v.impact}): ${v.help} — ${v.nodes.length} node(s)`)).toEqual([]);
}

test('UX-01 accessibilité : catalogue, fiche produit et panier, avec contenu @QR-US-01', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const p = await createProduct(request, staff, {
    name: `Carnet ${id}`, price_cents: 900, stock: 5, category_id: await createCategory(request, staff, `Cat ${id}`),
  });
  await page.goto('/');
  await expect(page.getByRole('link', { name: p.name })).toBeVisible(); // the grid has product cards
  await audit(page, info, 'catalogue');
  await page.getByRole('link', { name: p.name }).click();
  await expect(page.getByRole('heading', { level: 1, name: p.name })).toBeVisible();
  await audit(page, info, 'fiche-produit');
  await page.getByRole('button', { name: 'Ajouter au panier' }).click();
  await page.getByRole('link', { name: 'Voir le panier' }).click();
  await expect(page.getByRole('cell', { name: p.name })).toBeVisible();
  await audit(page, info, 'panier');
});

test('UX-01 accessibilité : back-office (commandes, produits, dialogue, erreurs de champ) @QR-US-01', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const p = await createProduct(request, staff, {
    name: `Agrafeuse ${id}`, price_cents: 1500, stock: 9, category_id: await createCategory(request, staff, `Cat ${id}`),
  });
  const ana = await registerCustomer(request, info);
  const order = await placeOrder(request, ana.token, [{ product_id: p.id, quantity: 1 }]);

  await uiLogin(page, STAFF.email, STAFF.password);
  await page.goto('/back-office/commandes');
  await expect(page.locator(`tr[data-order-id="${order.id}"]`).getByRole('button').first()).toBeVisible(); // rows + buttons
  await audit(page, info, 'back-office-commandes');

  await page.goto('/back-office/produits');
  await page.getByRole('searchbox', { name: 'Filtrer' }).fill(id);
  await expect(page.getByRole('row').filter({ hasText: p.name })).toBeVisible();
  await audit(page, info, 'gestion-produits');

  await page.getByRole('button', { name: `Supprimer ${p.name}` }).click();
  await expect(page.getByRole('dialog', { name: 'Supprimer le produit ?' })).toBeVisible();
  await audit(page, info, 'dialogue-confirmation');
  await page.getByRole('dialog').getByRole('button', { name: 'Annuler' }).click();

  const form = page.getByRole('form', { name: 'Nouveau produit' });
  await form.getByRole('button', { name: 'Créer le produit' }).click(); // empty form: the API answers 422
  await expect(form.getByLabel('Nom')).toHaveAttribute('aria-invalid', 'true');
  await audit(page, info, 'formulaire-erreurs');
});
