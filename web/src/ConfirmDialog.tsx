import { useEffect, useId, useRef } from 'react';

type Props = {
  open: boolean;
  title: string;
  message: string;
  confirmLabel: string;
  onConfirm: () => void;
  onCancel: () => void;
};

/** Modal confirmation before a destructive action (Chapitre I: user error protection). Escape cancels. */
export default function ConfirmDialog({ open, title, message, confirmLabel, onConfirm, onCancel }: Props) {
  const ref = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const textId = useId();

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog ref={ref} aria-labelledby={titleId} aria-describedby={textId} onCancel={e => { e.preventDefault(); onCancel(); }}>
      <h2 id={titleId}>{title}</h2>
      <p id={textId}>{message}</p>
      <div className="actions">
        <button type="button" autoFocus onClick={onCancel}>Annuler</button>
        <button type="button" className="danger" onClick={onConfirm}>{confirmLabel}</button>
      </div>
    </dialog>
  );
}
