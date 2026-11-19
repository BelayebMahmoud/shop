import type { OrderStatus } from './api';

/** BR-05 as the back-office shows it: only the transitions allowed from the current status get a button. */
export const NEXT: Record<OrderStatus, { to: OrderStatus; label: string }[]> = {
  PLACED: [{ to: 'PAID', label: 'Marquer payée' }, { to: 'CANCELLED', label: 'Annuler' }],
  PAID: [{ to: 'SHIPPED', label: 'Marquer expédiée' }, { to: 'CANCELLED', label: 'Annuler' }],
  SHIPPED: [{ to: 'DELIVERED', label: 'Marquer livrée' }],
  DELIVERED: [],
  CANCELLED: [],
};

export const STATUS_LABEL: Record<OrderStatus, string> = {
  PLACED: 'Passée',
  PAID: 'Payée',
  SHIPPED: 'Expédiée',
  DELIVERED: 'Livrée',
  CANCELLED: 'Annulée',
};

type ValidationItem = { loc: (string | number)[]; msg: string; type: string; ctx?: Record<string, unknown> };

function frenchMessage(err: ValidationItem): string {
  switch (err.type) {
    case 'missing':
    case 'string_too_short':
      return 'Ce champ est obligatoire.';
    case 'string_too_long':
      return `Au plus ${err.ctx?.max_length} caractères.`;
    case 'greater_than_equal':
      return `La valeur doit être supérieure ou égale à ${err.ctx?.ge}.`;
    case 'less_than_equal':
      return `La valeur doit être inférieure ou égale à ${err.ctx?.le}.`;
    case 'int_type':
    case 'int_parsing':
    case 'int_from_float':
    case 'value_error':
      return 'Un nombre entier est attendu.';
    case 'string_pattern_mismatch':
      return 'Format invalide (pas d’espace ni de caractère spécial).';
    default:
      return 'Valeur invalide.';
  }
}

/** Field-level messages from a 422 (FastAPI `detail` list) or a 409 DUPLICATE (`detail.field`). */
export function fieldErrors(detail: unknown): Record<string, string> {
  const out: Record<string, string> = {};
  if (Array.isArray(detail)) {
    for (const err of detail as ValidationItem[]) {
      const field = String(err.loc[err.loc.length - 1]);
      out[field] ??= frenchMessage(err);
    }
  } else if (detail && typeof detail === 'object' && (detail as { code?: string }).code === 'DUPLICATE') {
    out[(detail as { field: string }).field] = 'Cette valeur est déjà utilisée.';
  }
  return out;
}
