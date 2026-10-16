// Pieces of a commit shared by the commit page and "Guess the message": the meta line, the
// --stat, the files left out of the diff, and the diff itself with one collapsible block per file.
SD.historyUi = (() => {
  const { h } = SD.dom;
  const STATUS = { added: "added", modified: "modified", deleted: "deleted", renamed: "moved" };

  const module = () => SD.data.module("history");
  const record = () => SD.store.draft("history.guess") || {};

  function dateText(commit) {
    const ts = Date.parse(commit.git.date);
    return `${SD.util.dayLabel(ts)} ${new Date(ts).getFullYear()}`;
  }

  // "commit 9 of 20"
  function position(commits, commit) {
    return `commit ${commits.indexOf(commit) + 1} of ${commits.length}`;
  }

  const kindChip = (kind) => SD.ui.chip(kind, "none");
  const tagChip = (tag) => h("span", { class: "chip chip-tag", text: tag });

  // The --stat with its bars split: + in the added colour, - in the removed one.
  function stat(commit) {
    return h(
      "div",
      { class: "code hist-stat" },
      h("span", { class: "code-lang", "aria-hidden": "true", text: "--stat" }),
      h(
        "pre",
        { tabindex: "0", role: "group", "aria-label": "git show --stat" },
        h(
          "code",
          {},
          SD.history
            .statRows(commit.git.stat)
            .map((row) =>
              h(
                "span",
                { class: "stat-row" },
                row.lead,
                row.plus ? h("span", { class: "stat-add", text: row.plus }) : null,
                row.minus ? h("span", { class: "stat-del", text: row.minus }) : null,
                "\n",
              ),
            ),
        ),
      ),
    );
  }

  const HIDDEN_WHY = { "uv.lock": "which uv writes for you", "expenses.csv": "the expense data" };

  // uv.lock and expenses.csv count in the --stat but are left out of the diff.
  function hiddenNote(commit) {
    const hidden = commit.git.hidden;
    if (!hidden.length) return null;
    const parts = hidden.map((f) => {
      const why = HIDDEN_WHY[f.path.split("/").pop()];
      return `${f.path} (+${f.added} −${f.removed})${why ? `, ${why}` : ""}`;
    });
    return h(
      "p",
      { class: "fine hist-hidden" },
      `Left out of the diff below: ${parts.join("; ")}. The --stat above still counts ` +
        `${hidden.length === 1 ? "it" : "them"}.`,
    );
  }

  function fileBlock(file) {
    const path = file.old_path ? `${file.old_path} → ${file.path}` : file.path;
    const counts = h(
      "span",
      { class: "hist-counts" },
      h("span", { class: "stat-add", text: `+${file.added}` }),
      " ",
      h("span", { class: "stat-del", text: `−${file.removed}` }),
    );
    let extra = null;
    if (file.lines === 0) extra = h("span", { class: "hist-file-note", text: "empty file" });
    else if (file.collapsed)
      extra = h("span", { class: "hist-file-note", text: `long: ${file.lines} lines` });
    return h(
      "details",
      { class: "hist-file", open: !file.collapsed },
      h(
        "summary",
        {},
        h("span", { class: "hist-file-status", text: STATUS[file.status] || file.status }),
        h("span", { class: "hist-file-path", text: path }),
        counts,
        extra,
      ),
      h("div", { class: "hist-file-body", html: file.html }),
    );
  }

  // Every file's diff, with buttons to open or close them all.
  function diff(commit) {
    const blocks = commit.git.files.map(fileBlock);
    const setAll = (open) => blocks.forEach((b) => (b.open = open));
    return h(
      "div",
      { class: "hist-diff" },
      blocks.length > 1
        ? h(
            "div",
            { class: "hist-diff-tools" },
            SD.ui.button("Open every file", { kind: "quiet", onClick: () => setAll(true) }),
            SD.ui.button("Close every file", { kind: "quiet", onClick: () => setAll(false) }),
          )
        : null,
      blocks,
    );
  }

  return { module, record, dateText, position, kindChip, tagChip, stat, hiddenNote, diff };
})();
