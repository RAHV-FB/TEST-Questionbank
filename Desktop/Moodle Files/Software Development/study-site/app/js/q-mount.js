// SD.q.mount(container, question, opts): the one entry point for showing a question anywhere.
// Returns a controller {el, done(), key(event)}; see app/API.md for opts and callbacks.
SD.q.mount = (container, q, opts = {}) => {
  const mount = { mcq: SD.q.mcq, open: SD.q.open, sort: SD.q.sort }[q.type];
  if (!mount) throw new Error(`unknown question type ${q.type} (${q.id})`);
  return mount(container, q, opts);
};
