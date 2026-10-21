// The route (home): how he marks, the clock, and the 6-hour route as a timed timeline.
(() => {
  const { h } = CR.dom;
  const MIN = CR.util.MINUTE;

  const KIND_LABEL = {
    intro: "read",
    baseline: "paper",
    type: "sample, method and practice",
    break: "break",
    paper: "paper",
    review: "review",
    mistakes: "redo",
    final: "read",
  };

  function typeStatus(tid) {
    const t = CR.data.type(tid);
    if (!t) return "Not in this build";
    const lead = t.sample ? `His question: ${CR.store.sample(tid).shown ? "answer seen" : "not opened"}. ` : "";
    const sess = CR.store.session(tid);
    if (!sess) return `${lead}Practice: ${t.practice.length} questions, not started`;
    const sum = CR.mistakes.sessionSummary(sess);
    if (sum.finished) return `${lead}Practice done: ${sum.right} of ${sum.total} right`;
    return `${lead}Practice: ${sess.i} of ${sum.total} done`;
  }

  function paperStatus(pid) {
    const papers = CR.store.get().papers;
    const running = CR.paper.running(papers);
    if (running && running.paper === pid) return "In progress";
    const last = CR.paper.lastDone(papers, pid);
    if (!last) return "Not sat yet";
    return `Last: ${last.score}/${last.max}${last.to_mark ? ` (${last.to_mark} to mark)` : ""}`;
  }

  function statusOf(stop) {
    switch (stop.kind) {
      case "type":
        return typeStatus(stop.ref);
      case "baseline":
      case "paper":
        return paperStatus(stop.ref);
      case "review": {
        const last = CR.paper.lastDone(CR.store.get().papers, stop.ref);
        return last ? `${last.score}/${last.max}, open it to review` : "Sit the paper first";
      }
      case "mistakes": {
        const n = CR.mistakes.queue(CR.store.get().q, CR.data.knownIds).length;
        return n === 0 ? "Nothing to redo yet" : `${CR.util.plural(n, "question")} to redo`;
      }
      default:
        return "";
    }
  }

  function paceText(p) {
    switch (p.state) {
      case "before":
        return `Starts in ${CR.util.minutesLabel(p.minutes)}`;
      case "on":
        return "On pace";
      case "ahead":
        return `${CR.util.minutesLabel(p.minutes)} ahead`;
      case "behind":
        return `${CR.util.minutesLabel(p.minutes)} behind`;
      default:
        return "Route finished";
    }
  }

  function render({ root }) {
    const state = CR.store.get();
    if (!state.start) CR.store.setStart(CR.clock.defaultStart(Date.now()));
    const stops = CR.data.stops;
    const startTs = () => CR.store.get().start?.ts ?? CR.clock.defaultStart(Date.now());

    // ---- the clock and the progress
    const timeInput = h("input", {
      type: "time",
      id: "start-time",
      class: "time-input",
      value: CR.util.timeOfDay(startTs()),
      onchange: (e) => {
        const ts = CR.util.timeFromInput(e.target.value, Date.now());
        if (ts !== null) CR.store.setStart(ts);
      },
    });
    const nowButton = CR.ui.button("Now", {
      kind: "quiet",
      onClick: () => {
        CR.store.setStart(CR.clock.defaultStart(Date.now()));
        timeInput.value = CR.util.timeOfDay(startTs());
      },
    });
    const panel = h("div", { class: "clock-panel" });
    const upnext = h("div", { class: "upnext" });
    const rows = new Map();

    function paintPanel() {
      const now = Date.now();
      const s = CR.store.get();
      const prog = CR.clock.progress(stops, s.done);
      const p = CR.clock.pace(stops, s.done, startTs(), now);
      const planned = CR.clock.plannedEnd(stops, startTs());
      const figures = [
        h(
          "div",
          { class: "figure" },
          h("label", { class: "label", for: "start-time", text: "Start time" }),
          h("div", { class: "figure-row" }, timeInput, nowButton),
        ),
        h(
          "div",
          { class: "figure" },
          h("p", { class: "label", text: "Planned finish" }),
          h("p", { class: "figure-value", text: CR.clock.label(planned, startTs()) }),
          p.state === "behind" && prog.remaining > 0
            ? h("p", { class: "fine", text: `At this pace: ${CR.clock.label(CR.clock.projectedEnd(stops, s.done, now), startTs())}` })
            : null,
        ),
        h(
          "div",
          { class: "figure" },
          h("p", { class: "label", text: "Pace" }),
          h("p", { class: `figure-value pace-${p.state}`, text: paceText(p) }),
        ),
      ];
      CR.dom.fill(
        panel,
        h("div", { class: "figures" }, figures),
        CR.ui.progress(prog.count, prog.total, "Stops done"),
        h("p", { class: "fine progress-note", text: `${CR.util.minutesLabel(prog.minutes)} of ${CR.util.minutesLabel(prog.totalMinutes)} done, ${CR.util.minutesLabel(prog.remaining)} to go` }),
      );
      paintUpNext();
    }

    function paintUpNext() {
      const s = CR.store.get();
      const i = CR.clock.nextIndex(stops, s.done);
      const running = CR.paper.running(s.papers);
      const schedule = CR.clock.schedule(stops, startTs());
      const parts = [];
      if (running) {
        const left = CR.paper.timeLeft(running, Date.now());
        parts.push(
          h(
            "div",
            { class: "notice paper-running" },
            h("strong", { text: `${running.title} is running. ` }),
            `${CR.util.clock(left)} left. `,
            h("a", { href: CR.route.href("sit", running.id), text: "Go back to the paper" }),
          ),
        );
      }
      if (i === -1) {
        parts.push(h("p", { class: "lead", text: "Every stop is done. Sleep, eat, and read the answer formula once more before 14:00." }));
      } else {
        const stop = stops[i];
        const when = schedule[i];
        parts.push(
          h(
            "div",
            { class: "continue" },
            h("p", { class: "label", text: "Up next" }),
            h("p", { class: "continue-title", text: stop.title }),
            h("p", { class: "fine", text: `${CR.util.minutesLabel(stop.minutes)}, planned ${CR.clock.label(when.start, startTs())} to ${CR.clock.label(when.end, startTs())}. ${stop.note}` }),
            h("div", { class: "actions" }, CR.ui.linkButton("Continue", stop.href, "primary")),
          ),
        );
      }
      CR.dom.fill(upnext, parts);
    }

    // ---- the timeline
    function paintRow(stop, i) {
      const r = rows.get(stop.id);
      const s = CR.store.get();
      const done = CR.clock.isDone(s.done, stop.id);
      const next = i === CR.clock.nextIndex(stops, s.done);
      const when = CR.clock.schedule(stops, startTs())[i];
      r.li.className = `stop kind-${stop.kind}${done ? " is-done" : ""}${next ? " is-next" : ""}`;
      r.box.checked = done;
      r.clock.textContent = CR.clock.label(when.start, startTs());
      r.status.textContent = statusOf(stop);
      r.next.hidden = !next;
    }

    const list = h(
      "ol",
      { class: "timeline" },
      stops.map((stop) => {
        const id = `stop-${stop.id}`;
        const box = h("input", {
          type: "checkbox",
          "aria-labelledby": `${id}-title`,
          onchange: (e) => {
            CR.store.setDone(stop.id, e.target.checked);
            stops.forEach(paintRow);
            paintPanel();
          },
        });
        const clock = h("span", { class: "stop-clock" });
        const status = h("p", { class: "stop-status" });
        const next = CR.ui.chip("next", "warn");
        const li = h(
          "li",
          { class: "stop" },
          h("label", { class: "stop-tick" }, box),
          h("div", { class: "stop-time" }, clock, h("span", { class: "stop-min", text: CR.util.minutesLabel(stop.minutes) })),
          h(
            "div",
            { class: "stop-body" },
            h(
              "p",
              { class: "stop-head" },
              h("a", { class: "stop-title", id: `${id}-title`, href: stop.href, text: stop.title }),
              next,
            ),
            h("p", { class: "stop-kind label", text: stop.tid ? `${stop.tid} · ${KIND_LABEL[stop.kind]}` : KIND_LABEL[stop.kind] }),
            h("p", { class: "stop-note", text: stop.note }),
            status,
          ),
        );
        rows.set(stop.id, { li, box, clock, status, next });
        return li;
      }),
    );
    stops.forEach(paintRow);

    // ---- the page
    const introDone = CR.clock.isDone(state.done, "intro-intro");
    const box = h(
      "details",
      { class: "fold exam-fold", open: !introDone },
      h("summary", { class: "fold-summary" }, h("span", { class: "fold-title", text: "How he marks" })),
      CR.examBox(),
    );
    const missing = CR.data.meta.missing || [];

    root.append(
      h(
        "div",
        { class: "page-wide home" },
        h("h1", { text: "SWDev 6-Hour Cram" }),
        h("p", { class: "lead", text: "Built on his nine sample questions: what each one asks, what type of question it is, and the level of answer that earns full marks. One route, in order, just under six hours." }),
        CR.data.meta.mode !== "full"
          ? h("p", { class: "notice" }, `This is ${CR.data.meta.mode === "example" ? "an" : "a"} ${CR.data.meta.mode} build${missing.length ? `: ${missing.join(", ")} not included` : ""}.`)
          : null,
        upnext,
        panel,
        box,
        h("h2", { text: "The route" }),
        list,
        h("div", { class: "reset" }, resetControl()),
      ),
    );
    paintPanel();

    const timer = window.setInterval(() => {
      paintPanel();
      stops.forEach(paintRow);
    }, 30 * 1000);
    const off = CR.store.subscribe((_, kind) => {
      if (kind === "start" || kind === "all") {
        stops.forEach(paintRow);
        paintPanel();
      }
    });
    return {
      title: "Route",
      cleanup() {
        window.clearInterval(timer);
        off();
      },
    };
  }

  // Start again: deletes every answer, mistake, paper and tick on this device, after one confirmation.
  function resetControl() {
    const holder = h("div", { class: "reset-row" });
    const ask = () =>
      CR.dom.fill(
        holder,
        h("p", { class: "fine", text: "This deletes every answer, mistake, paper and tick on this device." }),
        CR.ui.button("Delete everything", {
          kind: "secondary",
          onClick: () => {
            CR.store.reset();
            CR.router.refresh();
          },
        }),
        CR.ui.button("Keep it", { kind: "quiet", onClick: idle }),
      );
    const idle = () => CR.dom.fill(holder, CR.ui.button("Start again from zero", { kind: "quiet", onClick: ask }));
    idle();
    return holder;
  }

  CR.router.register("home", { nav: "home", render });
})();
