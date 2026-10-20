// Pure route parsing and the link each stop of the 12-hour route opens. A route is tokens joined
// by "." (the Artifact viewer only passes #[A-Za-z0-9._~-]+), e.g. "type.T07.practice".
CR.route = (() => {
  const ROUTE = /^[A-Za-z0-9._~-]*$/;
  const TOKEN = /^[A-Za-z0-9_~-]+$/;
  const HOME = Object.freeze({ view: "home", args: Object.freeze([]), route: "home" });

  // "#type.T07" or "type.T07" -> {view: "type", args: ["T07"], route: "type.T07"};
  // "" -> home; a hash with any other character -> null.
  function parse(hash) {
    const raw = String(hash ?? "").replace(/^#/, "");
    if (!ROUTE.test(raw)) return null;
    const tokens = raw.split(".").filter(Boolean);
    if (tokens.length === 0) return HOME;
    return { view: tokens[0], args: tokens.slice(1), route: tokens.join(".") };
  }

  // build("type", "T07", "practice") -> "type.T07.practice". A bad token is a programming error.
  function build(...tokens) {
    for (const token of tokens) {
      if (!TOKEN.test(String(token))) throw new TypeError(`bad route token ${JSON.stringify(token)}`);
    }
    return tokens.join(".");
  }

  const href = (...tokens) => "#" + build(...tokens);

  // The route (no "#") that opens a stop of the 12-hour route.
  function stopRoute(stop) {
    switch (stop.kind) {
      case "intro":
        return build("start");
      case "baseline":
      case "paper":
        return build("paper", stop.ref);
      case "type":
        return build("type", stop.ref);
      case "break":
        return build("break", stop.ref);
      case "review":
        return build("review", stop.ref);
      case "mistakes":
        return build("mistakes");
      case "final":
        return build("final");
      default:
        throw new RangeError(`unknown stop kind ${stop.kind}`);
    }
  }

  const stopHref = (stop) => "#" + stopRoute(stop);

  return { parse, build, href, stopRoute, stopHref };
})();
