// Optional claude.ai capabilities. Outside a claude.ai Artifact window.claude is absent and every
// capability resolves null; inside one, use() may resolve late or never. Nothing waits on these.
SD.claude = (() => {
  const requests = new Map();
  const HIDE_FOR_VISIT = new Set([
    "not_granted",
    "sampling_disabled",
    "not_declared",
    "capability_disabled",
    "capability_removed",
  ]);
  const MARK_TIMEOUT_MS = 90 * 1000;
  let markingRefused = false;

  // The promise's result, or a rejection with code "timeout" when it takes longer than `ms`.
  function withTimeout(promise, ms) {
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(Object.assign(new Error("timeout"), { code: "timeout" })), ms);
      promise.then(
        (value) => {
          clearTimeout(timer);
          resolve(value);
        },
        (error) => {
          clearTimeout(timer);
          reject(error);
        },
      );
    });
  }

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

  // Memoised per name: capability("db"), capability("user"), capability("sample").
  function capability(name) {
    if (!requests.has(name)) requests.set(name, request(name));
    return requests.get(name);
  }

  // Resolves true when "Mark my answer with Claude" can be offered. Asking costs nothing.
  async function canMark() {
    const sample = await capability("sample");
    return Boolean(sample && typeof sample.json === "function") && !markingRefused;
  }

  // Content HTML -> plain text for the prompt, keeping line breaks of paragraphs and code.
  function textOf(html) {
    const box = document.createElement("div");
    box.innerHTML = html;
    box.querySelectorAll(".code-lang").forEach((el) => el.remove());
    box.querySelectorAll(".dline, p, li, pre, tr, h2, h3, h4").forEach((el) => el.append("\n"));
    return box.textContent.replace(/\n{3,}/g, "\n\n").trim();
  }

  function plainQuestion(q) {
    return {
      stem: textOf(q.stem_html),
      lines: q.lines || "5–8",
      parts: q.parts.map((p) => ({
        label: p.label,
        prompt: textOf(p.prompt_html),
        marks: p.marks,
        model: textOf(p.model_answer_html),
        rubric: p.rubric.map(textOf),
      })),
    };
  }

  // Resolves {result} or {error, hide}: hide means do not offer the button again this visit.
  async function mark(q, answers) {
    const sample = await capability("sample");
    if (!sample) return { error: "Claude is not available here.", hide: true };
    const plain = plainQuestion(q);
    try {
      const reply = await withTimeout(sample.json(SD.marking.request(plain, answers)), MARK_TIMEOUT_MS);
      return { result: SD.marking.parse(reply, plain) };
    } catch (e) {
      const code = e && typeof e.code === "string" ? e.code : null;
      if (code && HIDE_FOR_VISIT.has(code)) {
        markingRefused = true;
        return { error: "Claude marking is not available for this page.", hide: true };
      }
      if (code === "rate_limited") {
        return { error: "Claude is busy or your usage limit is reached. Try again later." };
      }
      if (code === "cancelled") return { error: "Marking was cancelled." };
      if (code === "timeout") return { error: "Claude did not answer in time. Try again, or mark it yourself." };
      if (code) return { error: "Claude could not mark this answer. Try again, or mark it yourself." };
      return { error: "Claude's reply did not match the rubric format. Try again." };
    }
  }

  return { capability, canMark, mark };
})();
