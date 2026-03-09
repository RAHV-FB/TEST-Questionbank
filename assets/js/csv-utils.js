/**
 * csv-utils.js
 * Robust CSV parser that handles:
 *  - Quoted fields (including HTML with commas and newlines)
 *  - Double-quote escaping within quoted fields ("")
 *  - Windows and Unix line endings
 */

const QUESTION_HEADERS = [
  'subject','topic','subtopic','question_index','sub_index',
  'question_type','question_text','option_a','option_b','option_c','option_d',
  'correct_option','markscheme','marks','image_path','difficulty','year','paper','notes'
];

/**
 * Parse a raw CSV string into an array of row arrays.
 * Each row is an array of field strings.
 */
function parseCSVRaw(text) {
  const rows = [];
  let i = 0;
  const len = text.length;

  // Normalise line endings
  text = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');

  while (i < len) {
    const row = [];
    // skip blank lines between rows (but keep empty fields within rows)
    while (i < len && text[i] === '\n') i++;
    if (i >= len) break;

    while (i < len && text[i] !== '\n') {
      if (text[i] === '"') {
        // Quoted field
        i++; // skip opening quote
        let field = '';
        while (i < len) {
          if (text[i] === '"') {
            if (i + 1 < len && text[i + 1] === '"') {
              // Escaped double-quote
              field += '"';
              i += 2;
            } else {
              i++; // skip closing quote
              break;
            }
          } else {
            field += text[i];
            i++;
          }
        }
        row.push(field);
        // skip comma or end of line
        if (i < len && text[i] === ',') i++;
      } else {
        // Unquoted field
        let field = '';
        while (i < len && text[i] !== ',' && text[i] !== '\n') {
          field += text[i];
          i++;
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
 * Parse a CSV string into an array of objects using the first row as headers.
 */
function parseCSV(text) {
  const rows = parseCSVRaw(text);
  if (rows.length === 0) return [];
  const headers = rows[0].map(h => h.trim().toLowerCase().replace(/\s+/g, '_'));
  return rows.slice(1).map(row => {
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = row[idx] !== undefined ? row[idx] : '';
    });
    return obj;
  }).filter(obj => obj.subject || obj.question_text); // skip empty rows
}

/**
 * Build a unique ID for a question row.
 * Format: {subject_lower}_{question_index}_{sub_index}
 * E.g.:  biology_4_a  |  chemistry_5_b  |  physics_1_
 */
function questionId(q) {
  const subj = (q.subject || '').toLowerCase().replace(/\s+/g, '-');
  const idx  = (q.question_index || '').toString().trim();
  const sub  = (q.sub_index || '').toString().trim();
  return `${subj}_${idx}_${sub}`;
}

/**
 * Group question rows into logical questions.
 * Questions with the same question_index are grouped as parts.
 * Returns array of { mainIndex, subject, topic, subtopic, parts[] }
 * where each part is a raw CSV row object.
 */
function groupQuestions(rows) {
  const groups = new Map(); // question_index → { ... }
  const order  = [];        // preserve insertion order of question_index

  rows.forEach(row => {
    const idx = (row.question_index || '').toString().trim();
    if (!idx) return;
    if (!groups.has(idx)) {
      groups.set(idx, {
        mainIndex: idx,
        subject:   row.subject,
        topic:     row.topic,
        subtopic:  row.subtopic,
        parts: []
      });
      order.push(idx);
    }
    groups.get(idx).parts.push(row);
  });

  return order.map(idx => groups.get(idx));
}

/**
 * Return a normalised question_type label.
 */
function normaliseType(type) {
  const t = (type || '').toLowerCase().replace(/\s+/g,'');
  if (t.includes('mcq') || t.includes('multiple')) return 'MCQ';
  if (t.includes('long'))   return 'Long Answer';
  if (t.includes('short'))  return 'Short Answer';
  if (t.includes('struct')) return 'Structured';
  return type || 'Short Answer';
}

/**
 * Return CSS class suffix for a question type.
 */
function typeCSSClass(type) {
  const t = normaliseType(type);
  if (t === 'MCQ')          return 'mcq';
  if (t === 'Long Answer')  return 'long';
  if (t === 'Short Answer') return 'short';
  return 'structured';
}

/**
 * Return CSS class suffix for a badge type.
 */
function typeBadgeClass(type) {
  return 'badge-' + typeCSSClass(type);
}
