/**
 * csv-utils.js
 * CSV parser + schema normaliser for the IB Question Bank.
 *
 * Real IB data schema columns:
 *   uniqueid, path, text_body, answer_type, question_type,
 *   mark_scheme, needs_context, exam, subject, section, topic,
 *   order, marks, parent_id, is_root, reference_code, subtopic,
 *   level, paper, command_term
 */

/* -----------------------------------------------
   Low-level CSV parser (handles quoted HTML fields)
   ----------------------------------------------- */
function parseCSVRaw(text) {
  const rows = [];
  text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
  let i = 0;
  const len = text.length;

  while (i < len) {
    while (i < len && text[i] === '\n') i++;
    if (i >= len) break;

    const row = [];
    while (i < len && text[i] !== '\n') {
      if (text[i] === '"') {
        i++;
        let field = '';
        while (i < len) {
          if (text[i] === '"') {
            if (i + 1 < len && text[i + 1] === '"') {
              field += '"'; i += 2;
            } else {
              i++; break;
            }
          } else {
            field += text[i++];
          }
        }
        row.push(field);
        if (i < len && text[i] === ',') i++;
      } else {
        let field = '';
        while (i < len && text[i] !== ',' && text[i] !== '\n') {
          field += text[i++];
        }
        row.push(field.trim());
        if (i < len && text[i] === ',') i++;
      }
    }
    if (row.length > 0) rows.push(row);
  }
  return rows;
}

/**
 * Parse CSV into array of objects using first row as headers.
 * Normalises field names to lowercase with underscores.
 */
function parseCSV(text) {
  const rows = parseCSVRaw(text);
  if (rows.length === 0) return [];
  const headers = rows[0].map(h => h.trim().toLowerCase().replace(/\s+/g, '_'));
  return rows.slice(1)
    .map(row => {
      const obj = {};
      headers.forEach((h, idx) => { obj[h] = row[idx] !== undefined ? row[idx] : ''; });
      return obj;
    })
    .filter(obj => obj.uniqueid || obj.text_body); // skip blank rows
}

/* -----------------------------------------------
   Schema normalisation helpers
   ----------------------------------------------- */

/**
 * Parse the IB "path" field into section / topic / subtopic.
 * Format: "Section > Topic > Subtopic" (1–3 parts)
 */
function parsePath(path) {
  const parts = (path || '').split('>').map(s => s.trim());
  return {
    section:  parts[0] || '',
    topic:    parts[1] || parts[0] || '',
    subtopic: parts[2] || parts[1] || ''
  };
}

/**
 * Unique stable ID for a question row.
 * Uses uniqueid field (already unique across subjects).
 */
function questionId(q) {
  return (q.uniqueid || '').trim();
}

/**
 * Normalise question_type to a consistent display label.
 */
function normaliseType(type) {
  const t = (type || '').toUpperCase().trim();
  if (t === 'MCQ')  return 'MCQ';
  if (t === 'SFA')  return 'Short Answer';
  if (t === 'LFA')  return 'Long Answer';
  if (t.includes('STRUCT')) return 'Structured';
  if (t.includes('SHORT'))  return 'Short Answer';
  if (t.includes('LONG'))   return 'Long Answer';
  if (t.includes('MULTIPLE') || t.includes('MCQ')) return 'MCQ';
  return type || 'Answer';
}

/**
 * CSS badge class suffix for a normalised type label.
 */
function typeBadgeClass(type) {
  const t = normaliseType(type);
  if (t === 'MCQ')          return 'badge-mcq';
  if (t === 'Long Answer')  return 'badge-long';
  if (t === 'Short Answer') return 'badge-short';
  return 'badge-structured';
}

/**
 * Determine if a row is a root (top-level) question.
 * Root = no parent_id.
 */
function isRootQuestion(row) {
  return !(row.parent_id || '').trim();
}

/**
 * Group rows into logical questions.
 * Each entry = { root row } + its children (sub-parts).
 * Returns array of { root, children, pid (parsedPath), topic, subtopic }
 */
function groupQuestions(rows) {
  const byId    = {};
  const children = {};   // parent_id → [child rows]
  const rootRows = [];

  rows.forEach(r => {
    byId[r.uniqueid] = r;
    const pid = (r.parent_id || '').trim();
    if (pid) {
      if (!children[pid]) children[pid] = [];
      children[pid].push(r);
    } else {
      rootRows.push(r);
    }
  });

  return rootRows.map(root => {
    const pp = parsePath(root.path);
    return {
      id:       root.uniqueid,
      root,
      children: (children[root.uniqueid] || []).sort((a,b) =>
        parseInt(a.order||0,10) - parseInt(b.order||0,10)
      ),
      topic:    root.topic    || pp.topic,
      subtopic: root.subtopic || pp.subtopic,
      section:  root.section  || pp.section,
      pp
    };
  });
}

/**
 * Inject correct src into data-image-id img tags.
 * Replaces <img class="question-image" data-image-id="abc123" …/>
 * with     <img src="{baseURL}/images/{subjectKey}/abc123.png" class="question-image" …/>
 */
function injectImageSrc(html, baseURL, subjectKey) {
  if (!html) return '';
  return html.replace(
    /<img([^>]*?)data-image-id="([^"]+)"([^>]*?)\/>/g,
    (match, before, imageId, after) => {
      const src = `${baseURL}/images/${subjectKey}/${imageId}.png`;
      return `<img${before}src="${src}" data-image-id="${imageId}"${after} style="max-width:100%;height:auto;" loading="lazy" onerror="this.style.display='none'" />`;
    }
  );
}

/**
 * Clean up encoding artefacts in HTML text (Â spaces, etc.)
 */
function cleanHTML(html) {
  if (!html) return '';
  return html
    .replace(/Â /g, ' ')
    .replace(/â/g, '–')
    .replace(/â/g, '—')
    .replace(/â/g, '′')
    .replace(/Â·/g, '·')
    .replace(/Â°/g, '°')
    .replace(/Ã—/g, '×')
    .replace(/Ã·/g, '÷');
}
