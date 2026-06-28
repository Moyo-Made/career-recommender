import { useState, useRef, useEffect } from 'react';

/**
 * Searchable course picker: type to filter known courses, or enter a course that
 * isn't listed as free text. Selecting a listed course resolves to its exact
 * canonical string (so the backend relevance filter can match it); free text is
 * passed through and treated by the backend as "no field filter".
 *
 * Keyboard: ArrowUp/Down to move, Enter to choose, Escape to close.
 */
export default function CourseCombobox({ options, value, onChange, placeholder = 'Type or select your course…' }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState(value || '');
  const [active, setActive] = useState(0);
  const rootRef = useRef(null);

  // Close (and revert text to the committed value) when clicking away.
  useEffect(() => {
    function onDocMouseDown(e) {
      if (rootRef.current && !rootRef.current.contains(e.target)) {
        setOpen(false);
        setQuery(value || '');
      }
    }
    document.addEventListener('mousedown', onDocMouseDown);
    return () => document.removeEventListener('mousedown', onDocMouseDown);
  }, [value]);

  const q = query.trim().toLowerCase();
  const matches = q ? options.filter((o) => o.toLowerCase().includes(q)) : options;
  const exact = options.some((o) => o.toLowerCase() === q);

  // Build the rendered rows: matching courses, plus a free-text row when the
  // typed value isn't an exact known course.
  const items = matches.map((label) => ({ type: 'option', label }));
  if (query.trim() && !exact) {
    items.push({ type: 'other', label: query.trim() });
  }

  function commit(item) {
    onChange(item.label);
    setQuery(item.label);
    setOpen(false);
  }

  function onKeyDown(e) {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (!open) setOpen(true);
      setActive((i) => Math.min(i + 1, items.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (open && items[active]) commit(items[active]);
    } else if (e.key === 'Escape') {
      setOpen(false);
      setQuery(value || '');
    }
  }

  return (
    <div className="combobox" ref={rootRef}>
      <input
        className="combobox-input"
        type="text"
        value={query}
        placeholder={placeholder}
        autoComplete="off"
        onChange={(e) => { setQuery(e.target.value); setOpen(true); setActive(0); }}
        onFocus={() => setOpen(true)}
        onKeyDown={onKeyDown}
      />
      <span className="combobox-chevron" aria-hidden>▾</span>

      {open && (
        <ul className="combobox-list" role="listbox">
          {items.length === 0 && (
            <li className="combobox-empty">No matches — keep typing to enter it.</li>
          )}
          {items.map((item, i) => (
            <li
              key={`${item.type}-${item.label}`}
              role="option"
              aria-selected={item.label === value}
              className={
                'combobox-item' +
                (i === active ? ' active' : '') +
                (item.label === value ? ' selected' : '') +
                (item.type === 'other' ? ' combobox-other' : '')
              }
              onMouseEnter={() => setActive(i)}
              onMouseDown={(e) => { e.preventDefault(); commit(item); }}
            >
              {item.type === 'other' ? <span>Use “{item.label}”</span> : <span>{item.label}</span>}
              {item.label === value && <span className="combobox-check" aria-hidden>✓</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
