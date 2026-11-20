/**
 * User management screen, E2E-06 and E2E-07 (docs/cahier-de-test.md §4), on chromium, firefox and mobile.
 * Expected values come from the rules: FR-05 (ADMIN changes a role, deactivates; a deactivated account gets 401 on
 * login and on a token issued before — Q-08), BR-11 (409 LAST_ADMIN), FR-02 (the page is hidden from other roles).
 */
import { expect, test, type Page } from '@playwright/test';
import { ADMIN, STAFF, apiToken, registerCustomer, uiLogin } from './helpers';

type User = { id: number; email: string; role: string; is_active: boolean };
const auth = (token: string) => ({ Authorization: `Bearer ${token}` });

function userRow(page: Page, email: string) {
  return page.getByRole('row').filter({ hasText: email });
}

test('E2E-06 l’administrateur change un rôle puis désactive un compte avec confirmation @FR-05', async ({ page, request }, info) => {
  const bob = await registerCustomer(request, info);

  await uiLogin(page, ADMIN.email, ADMIN.password);
  await page.goto('/back-office/utilisateurs');
  await page.getByRole('searchbox', { name: 'Filtrer' }).fill(bob.email);
  const row = userRow(page, bob.email);
  await expect(row).toHaveCount(1);

  // Role change: CUSTOMER -> STAFF, then Bob can read the dashboard (SC-FR-05-1).
  await row.getByRole('combobox', { name: `Rôle de ${bob.email}` }).selectOption({ label: 'Personnel' });
  await row.getByRole('button', { name: `Changer le rôle de ${bob.email}` }).click();
  await expect(page.getByRole('status')).toContainText(`${bob.email} : rôle Personnel`);
  await expect(row.getByRole('combobox', { name: `Rôle de ${bob.email}` })).toHaveValue('STAFF');
  const staffToken = await apiToken(request, bob.email, bob.password);
  expect((await request.get('/api/dashboard', { headers: auth(staffToken) })).status()).toBe(200);

  // Deactivation: "Annuler" keeps the account, "Désactiver" in the dialog deactivates it (SC-FR-05-2).
  await row.getByRole('button', { name: `Désactiver ${bob.email}` }).click();
  const dialog = page.getByRole('dialog', { name: 'Désactiver le compte ?' });
  await dialog.getByRole('button', { name: 'Annuler' }).click();
  await expect(dialog).toBeHidden();
  await expect(row.getByTestId('state')).toHaveText('Actif');

  await row.getByRole('button', { name: `Désactiver ${bob.email}` }).click();
  await dialog.getByRole('button', { name: 'Désactiver' }).click();
  await expect(page.getByRole('status')).toContainText(`${bob.email} : compte désactivé`);
  await expect(row.getByTestId('state')).toHaveText('Désactivé');
  await expect(row.getByRole('button', { name: `Désactiver ${bob.email}` })).toHaveCount(0);

  const relogin = await request.post('/api/auth/login', { form: { username: bob.email, password: bob.password } });
  expect(relogin.status()).toBe(401);
  expect((await request.get('/api/auth/me', { headers: auth(staffToken) })).status()).toBe(401);
});

test('E2E-07 refus de retirer le dernier administrateur actif, page réservée à ADMIN @BR-11 @FR-02', async ({ page, request }) => {
  const adminToken = await apiToken(request, ADMIN.email, ADMIN.password);
  const all = await (await request.get('/api/users', { headers: auth(adminToken) })).json() as User[];
  const activeAdmins = all.filter(u => u.role === 'ADMIN' && u.is_active);
  expect(activeAdmins.map(u => u.email), 'précondition : Alice seule ADMIN active').toEqual([ADMIN.email]);

  await uiLogin(page, ADMIN.email, ADMIN.password);
  await page.goto('/back-office/utilisateurs');
  await page.getByRole('searchbox', { name: 'Filtrer' }).fill(ADMIN.email);
  const row = userRow(page, ADMIN.email);

  await row.getByRole('combobox', { name: `Rôle de ${ADMIN.email}` }).selectOption({ label: 'Personnel' });
  await row.getByRole('button', { name: `Changer le rôle de ${ADMIN.email}` }).click();
  await expect(page.getByRole('alert')).toContainText('au moins un administrateur actif');
  await expect(row.getByRole('combobox', { name: `Rôle de ${ADMIN.email}` })).toHaveValue('ADMIN');

  await row.getByRole('button', { name: `Désactiver ${ADMIN.email}` }).click();
  await page.getByRole('dialog', { name: 'Désactiver le compte ?' }).getByRole('button', { name: 'Désactiver' }).click();
  await expect(page.getByRole('alert')).toContainText('au moins un administrateur actif');
  await expect(row.getByTestId('state')).toHaveText('Actif');

  const me = await (await request.get('/api/auth/me', { headers: auth(adminToken) })).json() as User;
  expect(me).toMatchObject({ role: 'ADMIN', is_active: true }); // nothing changed

  // FR-02: STAFF neither sees the link nor gets the page.
  await page.getByRole('button', { name: 'Se déconnecter' }).click();
  await uiLogin(page, STAFF.email, STAFF.password);
  await expect(page.getByRole('link', { name: 'Utilisateurs' })).toHaveCount(0);
  await page.goto('/back-office/utilisateurs');
  await expect(page.getByRole('heading', { name: 'Accès refusé' })).toBeVisible();
  await expect(page.getByRole('table')).toHaveCount(0);
});
