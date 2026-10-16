// The content index. SD.indexContent(raw) is pure; SD.readContent() reads the build's data blob.
// main.js sets SD.data = SD.readContent(). See app/API.md for every accessor.
SD.indexContent = (raw) => {
  const modules = raw.modules.slice().sort((a, b) => a.order - b.order);
  const papers = raw.papers || [];
  const byModule = new Map();
  const bySection = new Map();
  const byQuestion = new Map();
  const byCard = new Map();
  const byPaper = new Map();
  const sectionQuestions = new Map();
  const bank = [];
  const cards = [];

  for (const mod of modules) {
    // The "predicted" chip says it wherever the title shows, so the title need not.
    if (mod.predicted) mod.title = mod.title.replace(/\s*\(predicted\)\s*$/i, "");
    byModule.set(mod.id, mod);
    mod.sections.forEach((section, index) => {
      section.mid = mod.id;
      section.index = index;
      section.token = section.id.slice(mod.id.length + 1);
      section.plain = SD.util.plain(section.heading);
      bySection.set(section.id, section);
      sectionQuestions.set(section.id, []);
    });
    for (const q of mod.questions) {
      q.mid = mod.id;
      byQuestion.set(q.id, q);
      bank.push(q);
    }
    for (const card of mod.flashcards) {
      card.mid = mod.id;
      byCard.set(card.id, card);
      cards.push(card);
    }
  }
  for (const paper of papers) {
    byPaper.set(paper.id, paper);
    for (const q of paper.questions) {
      q.mid = q.module_ref;
      q.paper = paper.id;
      byQuestion.set(q.id, q);
    }
  }
  for (const q of byQuestion.values()) sectionQuestions.get(q.section_ref)?.push(q.id);

  const section = (id) => bySection.get(id) || null;
  const sectionRoute = (id) => {
    const s = section(id);
    return s ? SD.route.build("learn", s.mid, s.token) : null;
  };

  return {
    meta: raw.meta,
    modules,
    papers,
    plan: raw.plan || [],
    glossary: raw.glossary || [],
    bank, // every module question, in course order
    cards, // every flashcard, in course order
    allQuestions: [...byQuestion.values()], // bank, then paper questions
    module: (id) => byModule.get(id) || null,
    section,
    question: (id) => byQuestion.get(id) || null,
    card: (id) => byCard.get(id) || null,
    paper: (id) => byPaper.get(id) || null,
    sectionQuestions: (id) => sectionQuestions.get(id) || [],
    sectionRoute,
  };
};

SD.readContent = () => {
  const el = document.getElementById("study-data");
  if (!el) throw new Error("the page has no #study-data block; rebuild it with tools/build.py");
  return SD.indexContent(JSON.parse(el.textContent));
};
