/**
 * SEC-02 (QR-SE-02, fiche 4): stored XSS in a product name. The script must show as text and never run.
 */
import { expect, test } from '@playwright/test';
import { STAFF, apiToken, createCategory, createProduct, uid } from './helpers';

test('SEC-02 XSS stocké dans un nom de produit : affiché comme texte, jamais exécuté @QR-SE-02', async ({ page, request }, info) => {
  const staff = await apiToken(request, STAFF.email, STAFF.password);
  const id = uid(info);
  const name = `<img src=x onerror="window.__xss=1"><script>window.__xss=1</script> ${id}`;
  const p = await createProduct(request, staff, { name, price_cents: 100, stock: 1, category_id: await createCategory(request, staff, `Cat ${id}`) });
  const dialogs: string[] = [];
  page.on('dialog', d => { dialogs.push(d.message()); d.dismiss(); });

  await page.goto('/');
  await page.getByRole('searchbox', { name: 'Rechercher' }).fill(id);
  await expect(page.getByRole('link', { name })).toBeVisible(); // the raw text is shown
  await page.goto(`/produits/${p.id}`);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(name);

  expect(await page.evaluate(() => (window as unknown as { __xss?: number }).__xss)).toBeUndefined();
  expect(await page.locator('main img, main script').count()).toBe(0); // no element was injected
  expect(dialogs).toEqual([]);
});
