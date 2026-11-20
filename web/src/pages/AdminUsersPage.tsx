import { useCallback, useEffect, useState } from 'react';
import { ApiError, changeRole, deactivateUser, getUsers, type Role, type User } from '../api';
import { useAuth } from '../auth';
import ConfirmDialog from '../ConfirmDialog';

const ROLE_LABEL: Record<Role, string> = { CUSTOMER: 'Client', STAFF: 'Personnel', ADMIN: 'Administrateur' };
const ROLES = Object.keys(ROLE_LABEL) as Role[];

type Message = { kind: 'status' | 'alert'; text: string };

/** BR-11 (409 LAST_ADMIN) gets its own message; anything else stays generic, the API is the judge (FR-02). */
function failure(user: User, e: unknown): Message {
  const why = e instanceof ApiError && e.code === 'LAST_ADMIN'
    ? 'refusé, il doit toujours rester au moins un administrateur actif'
    : 'erreur, rien n’a été modifié';
  return { kind: 'alert', text: `${user.email} : ${why}.` };
}

/** FR-05: ADMIN lists users, changes a role and deactivates an account (with confirmation). */
export default function AdminUsersPage() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[] | null>(null);
  const [filter, setFilter] = useState('');
  const [roles, setRoles] = useState<Record<number, Role>>({});
  const [toDeactivate, setToDeactivate] = useState<User | null>(null);
  const [message, setMessage] = useState<Message | null>(null);

  const load = useCallback(() => getUsers().then(list => { setUsers(list); setRoles({}); }), []);
  useEffect(() => { load(); }, [load]);

  const saveRole = async (u: User) => {
    const role = roles[u.id] ?? u.role;
    try {
      await changeRole(u.id, role);
      setMessage({ kind: 'status', text: `${u.email} : rôle ${ROLE_LABEL[role]}.` });
    } catch (e) {
      setMessage(failure(u, e));
    }
    load();
  };

  const confirmDeactivate = async () => {
    const u = toDeactivate;
    setToDeactivate(null);
    if (!u) return;
    try {
      await deactivateUser(u.id);
      setMessage({ kind: 'status', text: `${u.email} : compte désactivé.` });
    } catch (e) {
      setMessage(failure(u, e));
    }
    load();
  };

  const needle = filter.trim().toLowerCase();
  const shown = users?.filter(u => u.email.toLowerCase().includes(needle));
  return (
    <main>
      <h1>Utilisateurs</h1>
      <label>
        Filtrer{' '}
        <input type="search" value={filter} onChange={e => setFilter(e.target.value)} placeholder="Email" />
      </label>
      {message && <p role={message.kind}>{message.text}</p>}
      {!shown ? <p>Chargement…</p> : shown.length === 0 ? <p>Aucun utilisateur.</p> : (
        <table>
          <caption className="sr-only">Comptes utilisateurs</caption>
          <thead>
            <tr>
              <th scope="col">N°</th><th scope="col">Email</th><th scope="col">Rôle</th>
              <th scope="col">État</th><th scope="col">Actions</th>
            </tr>
          </thead>
          <tbody>
            {shown.map(u => {
              const selected = roles[u.id] ?? u.role;
              return (
                <tr key={u.id} data-user-id={u.id}>
                  <td>{u.id}</td>
                  <td>{u.email}{u.id === me?.id && <span className="muted"> (vous)</span>}</td>
                  <td>
                    <select
                      aria-label={`Rôle de ${u.email}`}
                      value={selected}
                      disabled={!u.is_active}
                      onChange={e => setRoles({ ...roles, [u.id]: e.target.value as Role })}
                    >
                      {ROLES.map(r => <option key={r} value={r}>{ROLE_LABEL[r]}</option>)}
                    </select>
                  </td>
                  <td data-testid="state">{u.is_active ? 'Actif' : 'Désactivé'}</td>
                  <td className="actions">
                    {u.is_active && (
                      <>
                        <button
                          type="button"
                          disabled={selected === u.role}
                          onClick={() => saveRole(u)}
                          aria-label={`Changer le rôle de ${u.email}`}
                        >
                          Changer le rôle
                        </button>
                        <button
                          type="button"
                          className="danger"
                          onClick={() => setToDeactivate(u)}
                          aria-label={`Désactiver ${u.email}`}
                        >
                          Désactiver
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
      <ConfirmDialog
        open={toDeactivate !== null}
        title="Désactiver le compte ?"
        message={toDeactivate ? `${toDeactivate.email} ne pourra plus se connecter et ses sessions en cours seront refusées.` : ''}
        confirmLabel="Désactiver"
        onConfirm={confirmDeactivate}
        onCancel={() => setToDeactivate(null)}
      />
    </main>
  );
}
