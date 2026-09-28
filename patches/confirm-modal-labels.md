# Confirm modal label fix

Remote update dialog used a red **Delete** button by mistake.

## What changed

| Dialog | Confirm button |
|--------|----------------|
| Remote update available | **Load remote** |
| Import data | **Import** |
| Delete page | **Delete page** (red) |
| Clear local data | **Clear data** (red) |
| Remove from library | **Remove** (red) |

## Quick fix on a running server

If your HTML already works (remote save OK), apply this minimal change.

### 1. Edit `showConfirmModal`

Replace the function so it accepts an options argument and uses a configurable label:

```javascript
function showConfirmModal(title, message, options) {
  const opts = options || {};
  const confirmLabel = opts.confirmLabel || 'OK';
  const confirmClass = opts.danger ? 'danger' : '';
  const titleColor = opts.danger ? '#f87171' : 'var(--accent)';

  return new Promise((resolve) => {
    const existing = document.querySelector('.modal-overlay');
    if (existing) existing.remove();

    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal-box">
        <h3 style="color: ${titleColor};">${title}</h3>
        <p>${message}</p>
        <div class="modal-actions">
          <button class="secondary" id="modalCancel">Cancel</button>
          <button class="${confirmClass}" id="modalConfirm">${confirmLabel}</button>
        </div>
      </div>
    `;
    document.body.appendChild(overlay);

    const cleanup = (result) => {
      overlay.remove();
      resolve(result);
    };

    overlay.querySelector('#modalConfirm').onclick = () => cleanup(true);
    overlay.querySelector('#modalCancel').onclick = () => cleanup(false);
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) cleanup(false);
    });
  });
}
```

### 2. Remote update call

Add the third argument:

```javascript
const ok = await showConfirmModal(
  'Remote update available',
  'The shared project was updated' + who + '.\n\nLoad the remote version now?\n(Your current unsaved block layout on this page may be replaced.)',
  { confirmLabel: 'Load remote' }
);
```

### 3. Delete / clear / remove calls

Pass `{ confirmLabel: '...', danger: true }` as appropriate (see table above).

Then hard-refresh the browser (`Ctrl+Shift+R`).
