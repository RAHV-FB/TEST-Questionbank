// Pure route parsing. A route is tokens joined by "." (the Artifact viewer only passes
// #[A-Za-z0-9._~-]+), e.g. "learn.testing-tdd.s3". The first token names the view.
SD.route = (() => {
  const ROUTE = /^[A-Za-z0-9._~-]*$/;
  const TOKEN = /^[A-Za-z0-9_~-]+$/;
  const HOME = Object.freeze({ view: "home", args: Object.freeze([]), route: "home" });

  // "#learn.scrum" or "learn.scrum" -> {view: "learn", args: ["scrum"], route: "learn.scrum"};
  // "" -> home; a hash with any other character -> null.
  function parse(hash) {
    const raw = String(hash ?? "").replace(/^#/, "");
    if (!ROUTE.test(raw)) return null;
    const tokens = raw.split(".").filter(Boolean);
    if (tokens.length === 0) return HOME;
    return { view: tokens[0], args: tokens.slice(1), route: tokens.join(".") };
  }

  // build("learn", "scrum", "s2") -> "learn.scrum.s2". A bad token is a programming error.
  function build(...tokens) {
    for (const token of tokens) {
      if (!TOKEN.test(String(token))) throw new TypeError(`bad route token ${JSON.stringify(token)}`);
    }
    return tokens.join(".");
  }

  function href(...tokens) {
    return "#" + build(...tokens);
  }

  return { parse, build, href };
})();
