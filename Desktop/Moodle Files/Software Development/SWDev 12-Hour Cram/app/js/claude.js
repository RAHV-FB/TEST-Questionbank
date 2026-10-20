// The optional Claude tutor. Outside a claude.ai Artifact window.claude is absent and the
// capability resolves null; inside one, use() may resolve late or never. Nothing waits on it, it is
// never called on load, and a call to Claude happens only on the student's click.
CR.claude = (() => {
  const requests = new Map();
  const HIDE_FOR_VISIT = new Set([
    "not_granted",
    "sampling_disabled",
    "not_declared",
    "capability_disabled",
    "capability_removed",
  ]);
  const TIMEOUT_MS = 150 * 1000;
  let refused = false;

  function request(name) {
    try {
      const host = window.claude;
      if (!host || typeof host.use !== "function") return Promise.resolve(null);
      return Promise.resolve(host.use(name)).then(
        (cap) => cap || null,
        () => null,
      );
    } catch {
      return Promise.resolve(null);
    }
  }

  // Memoised per name. Asking costs nothing: the viewer is asked only when a call is made.
  function capability(name) {
    if (!requests.has(name)) requests.set(name, request(name));
    return requests.get(name);
  }

  // Resolves true when "Ask Claude about this" can be offered.
  async function canAsk() {
    const sample = await capability("sample");
    return typeof sample === "function" && !refused;
  }

  // The plain-text form of a question for the prompt (see CR.tutor.request).
  function plainQuestion(q) {
    const t = CR.dom.textOf;
    const base = { type: q.type, stem: t(q.stem_html), explanation: t(q.explanation_html) };
    if (q.type === "mcq") return { ...base, options: q.options.map((o) => ({ text: t(o.text_html), correct: o.correct })) };
    if (q.type === "open") {
      return {
        ...base,
        parts: q.parts.map((p) => ({
          label: p.label,
          prompt: t(p.prompt_html),
          marks: p.marks,
          model: t(p.model_answer_html),
          rubric: p.rubric.map(t),
        })),
      };
    }
    return {
      ...base,
      categories: q.categories.map((c) => ({ id: c.id, label: c.label })),
      items: q.items.map((it) => ({ text: t(it.text_html), category: it.category })),
    };
  }

  const MESSAGES = {
    rate_limited: "Claude is busy or your usage limit is reached. Try again later.",
    cancelled: "Stopped.",
    timeout: "Claude did not answer in time. Try again.",
    prompt_too_large: "This question is too long to send.",
  };

  // Resolves {text} or {error, hide, partial}: hide means do not offer the button again this visit.
  async function ask(q, answer, typed, { onText, signal } = {}) {
    const sample = await capability("sample");
    if (typeof sample !== "function") return { error: "Claude is not available here.", hide: true };
    const control = new AbortController();
    const stop = () => control.abort();
    let timedOut = false;
    if (signal) signal.addEventListener("abort", stop);
    const timer = setTimeout(() => {
      timedOut = true;
      control.abort();
    }, TIMEOUT_MS);
    try {
      const prompt = CR.tutor.request(plainQuestion(q), answer, typed);
      const { text } = await sample(prompt, {
        modelTier: "quick",
        signal: control.signal,
        onText: ({ text: soFar }) => onText && onText(soFar),
      });
      return { text };
    } catch (e) {
      const code = timedOut ? "timeout" : e && typeof e.code === "string" ? e.code : null;
      const partial = e && typeof e.text === "string" ? e.text : "";
      if (code && HIDE_FOR_VISIT.has(code)) {
        refused = true;
        return { error: "Claude is not available for this page.", hide: true, partial };
      }
      return { error: MESSAGES[code] || "Claude could not answer. Try again.", partial };
    } finally {
      clearTimeout(timer);
      if (signal) signal.removeEventListener("abort", stop);
    }
  }

  return { capability, canAsk, ask, plainQuestion };
})();
