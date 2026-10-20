// Pure helpers: formatting, dates and clocks, seeded shuffling, the handwriting line estimate.
CR.util = (() => {
  const MINUTE = 60 * 1000;
  const DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const CHARS_PER_LINE = 60;
  const EXAM_TZ = "Europe/Madrid"; // the exam's own clock, whatever time zone the browser is in
  const formatters = new Map();

  const pad2 = (n) => String(n).padStart(2, "0");

  function plural(n, one, many = one + "s") {
    return `${n} ${n === 1 ? one : many}`;
  }

  function percent(part, whole) {
    return whole > 0 ? Math.round((part / whole) * 100) : 0;
  }

  // FNV-1a, 32 bit: a stable seed from a string such as "scrum-q03#2".
  function hashString(text) {
    let h = 0x811c9dc5;
    for (let i = 0; i < text.length; i += 1) {
      h ^= text.charCodeAt(i);
      h = Math.imul(h, 0x01000193) >>> 0;
    }
    return h;
  }

  // mulberry32: a small seeded generator, so a shuffle is the same every time for one seed.
  function seededRandom(seed) {
    let a = seed >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  function shuffled(list, seed) {
    const out = list.slice();
    const random = seededRandom(seed);
    for (let i = out.length - 1; i > 0; i -= 1) {
      const j = Math.floor(random() * (i + 1));
      [out[i], out[j]] = [out[j], out[i]];
    }
    return out;
  }

  // Handwritten lines a typed answer would take: about 60 characters per line, and every
  // paragraph starts a new line.
  function lineEstimate(text, perLine = CHARS_PER_LINE) {
    return String(text)
      .split("\n")
      .map((para) => para.trim().length)
      .reduce((sum, len) => sum + Math.ceil(len / perLine), 0);
  }

  // "5–8" or "5-8" -> {lo: 5, hi: 8}; anything else -> null.
  function parseRange(text) {
    const m = /^\s*(\d+)\s*[–-]\s*(\d+)\s*$/.exec(String(text));
    return m ? { lo: Number(m[1]), hi: Number(m[2]) } : null;
  }

  // A running clock as an invigilator's reads: "60:00", "59:59", "9:05". Seconds round up so
  // 0:00 means time is up.
  function clock(ms) {
    const total = Math.max(0, Math.ceil(ms / 1000));
    return `${Math.floor(total / 60)}:${pad2(total % 60)}`;
  }

  // Elapsed time in pytest's style: "52m10s", "1h02m", "45s".
  function duration(ms) {
    const total = Math.max(0, Math.round(ms / 1000));
    const h = Math.floor(total / 3600);
    const m = Math.floor((total % 3600) / 60);
    const s = total % 60;
    if (h > 0) return `${h}h${pad2(m)}m`;
    if (m > 0) return `${m}m${pad2(s)}s`;
    return `${s}s`;
  }

  // A length of study in minutes: "45 min", "1 h 05", "2 h".
  function minutesLabel(minutes) {
    const m = Math.max(0, Math.round(minutes));
    if (m < 60) return `${m} min`;
    const rest = m % 60;
    return rest === 0 ? `${Math.floor(m / 60)} h` : `${Math.floor(m / 60)} h ${pad2(rest)}`;
  }

  // Time left until an event: "7 d 18 h", "5 h 04 min", "12 min".
  function countdown(ms) {
    if (ms <= 0) return "0 min";
    const totalMinutes = Math.ceil(ms / MINUTE);
    const days = Math.floor(totalMinutes / (24 * 60));
    const hours = Math.floor((totalMinutes % (24 * 60)) / 60);
    const minutes = totalMinutes % 60;
    if (days > 0) return `${days} d ${hours} h`;
    if (hours > 0) return `${hours} h ${pad2(minutes)} min`;
    return `${minutes} min`;
  }

  // "07:40" in the browser's own time zone.
  function timeOfDay(ts) {
    const d = new Date(ts);
    return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
  }

  // "07:40" typed in a time field -> that time today (the day of `now`), else null.
  function timeFromInput(text, now) {
    const m = /^(\d{1,2}):(\d{2})$/.exec(String(text).trim());
    if (!m || Number(m[1]) > 23 || Number(m[2]) > 59) return null;
    const d = new Date(now);
    d.setHours(Number(m[1]), Number(m[2]), 0, 0);
    return d.getTime();
  }

  // Whole calendar days between two moments in the browser's time zone (DST safe).
  function dayDiff(ts, base) {
    const a = new Date(ts);
    const b = new Date(base);
    const da = Date.UTC(a.getFullYear(), a.getMonth(), a.getDate());
    const db = Date.UTC(b.getFullYear(), b.getMonth(), b.getDate());
    return Math.round((da - db) / (24 * 60 * MINUTE));
  }

  // Calendar fields of a moment in `timeZone` (the browser's own when none is given).
  function fields(ts, timeZone) {
    if (!timeZone) {
      const d = new Date(ts);
      return {
        year: d.getFullYear(),
        month: d.getMonth(),
        day: d.getDate(),
        hour: d.getHours(),
        minute: d.getMinutes(),
        weekday: d.getDay(),
      };
    }
    if (!formatters.has(timeZone)) {
      formatters.set(
        timeZone,
        new Intl.DateTimeFormat("en-GB", {
          timeZone,
          year: "numeric",
          month: "numeric",
          day: "numeric",
          hour: "numeric",
          minute: "numeric",
          hourCycle: "h23",
        }),
      );
    }
    const p = Object.fromEntries(formatters.get(timeZone).formatToParts(ts).map((x) => [x.type, x.value]));
    const year = Number(p.year);
    const month = Number(p.month) - 1;
    const day = Number(p.day);
    return {
      year,
      month,
      day,
      hour: Number(p.hour),
      minute: Number(p.minute),
      weekday: new Date(Date.UTC(year, month, day)).getUTCDay(),
    };
  }

  // "Thu 22 Oct, 14:00"; pass a time zone to read the date on another clock (the exam's).
  function dateTimeLabel(ts, timeZone = null) {
    const f = fields(ts, timeZone);
    return `${DAYS[f.weekday]} ${f.day} ${MONTHS[f.month]}, ${pad2(f.hour)}:${pad2(f.minute)}`;
  }

  return {
    MINUTE,
    EXAM_TZ,
    pad2,
    plural,
    percent,
    hashString,
    seededRandom,
    shuffled,
    lineEstimate,
    parseRange,
    clock,
    duration,
    minutesLabel,
    countdown,
    timeOfDay,
    timeFromInput,
    dayDiff,
    dateTimeLabel,
  };
})();
