// The page's content, indexed. CR.indexData(raw) takes the build's data block (see build_cram.py)
// and returns the accessors the views use; CR.data is set once at boot. No DOM here.
CR.indexData = (raw) => {
  const stops = raw.route.map((s) => ({
    ...s,
    tid: s.kind === "type" ? s.ref : null,
    href: CR.route.stopHref(s),
  }));
  const questions = raw.questions;
  const papers = raw.papers;
  const sampleIds = new Set(papers.find((p) => p.id === "sample")?.questions || []);
  return {
    meta: raw.meta,
    names: raw.names,
    intro: raw.intro,
    stops,
    types: raw.types,
    papers,
    questions,
    knownIds: new Set(Object.keys(questions)),
    stop: (id) => stops.find((s) => s.id === id) || null,
    type: (tid) => raw.types[tid] || null,
    question: (id) => questions[id] || null,
    paper: (id) => papers.find((p) => p.id === id) || null,
    paperQuestions: (paper) => paper.questions.map((id) => questions[id]).filter(Boolean),
    isSample: (id) => sampleIds.has(id),
    totalMinutes: stops.reduce((sum, s) => sum + s.minutes, 0),
  };
};
