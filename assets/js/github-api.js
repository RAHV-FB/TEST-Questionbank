/**
 * github-api.js
 * Minimal GitHub REST API v3 wrapper for reading and writing files.
 * Requires a Personal Access Token with `repo` or `contents:write` scope.
 *
 * Config is stored in localStorage under key "qb_gh_config".
 */

const GH_API = 'https://api.github.com';

class GitHubAPI {
  constructor(config) {
    // config: { token, owner, repo, branch }
    this.config = config;
  }

  get headers() {
    return {
      'Accept': 'application/vnd.github+json',
      'Authorization': `Bearer ${this.config.token}`,
      'X-GitHub-Api-Version': '2022-11-28',
      'Content-Type': 'application/json'
    };
  }

  get base() {
    const { owner, repo } = this.config;
    return `${GH_API}/repos/${owner}/${repo}/contents`;
  }

  /** Read a file; returns { content (decoded string), sha } or null on 404 */
  async readFile(path) {
    const { branch } = this.config;
    const url = `${this.base}/${path}?ref=${encodeURIComponent(branch)}`;
    const res = await fetch(url, { headers: this.headers });
    if (res.status === 404) return null;
    if (!res.ok) throw new Error(`GitHub read error ${res.status}: ${await res.text()}`);
    const data = await res.json();
    const content = atob(data.content.replace(/\n/g, ''));
    return { content, sha: data.sha, raw: data };
  }

  /**
   * Write (create or update) a file.
   * @param {string} path  - Repo-relative path e.g. "data/edits/changes.json"
   * @param {string} content - Raw string content
   * @param {string} message - Commit message
   * @param {string|null} sha - Current file SHA (required for updates, null to create)
   */
  async writeFile(path, content, message, sha = null) {
    const { branch } = this.config;
    const encoded = btoa(unescape(encodeURIComponent(content)));
    const body = { message, content: encoded, branch };
    if (sha) body.sha = sha;

    const res = await fetch(`${this.base}/${path}`, {
      method: 'PUT',
      headers: this.headers,
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error(`GitHub write error ${res.status}: ${await res.text()}`);
    return res.json();
  }

  /** Read a JSON file and parse it. Returns parsed object or null. */
  async readJSON(path) {
    const file = await this.readFile(path);
    if (!file) return null;
    try {
      return { data: JSON.parse(file.content), sha: file.sha };
    } catch {
      return { data: null, sha: file.sha };
    }
  }

  /** Write a JSON file with proper formatting. */
  async writeJSON(path, obj, message, sha = null) {
    return this.writeFile(path, JSON.stringify(obj, null, 2), message, sha);
  }

  // ---- Static config helpers ----

  static CONFIG_KEY = 'qb_gh_config';

  static loadConfig() {
    try {
      const raw = localStorage.getItem(GitHubAPI.CONFIG_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }

  static saveConfig(config) {
    localStorage.setItem(GitHubAPI.CONFIG_KEY, JSON.stringify(config));
  }

  static clearConfig() {
    localStorage.removeItem(GitHubAPI.CONFIG_KEY);
  }

  /** Create an API instance from saved config, or null if not configured. */
  static fromSaved() {
    const cfg = GitHubAPI.loadConfig();
    return cfg && cfg.token ? new GitHubAPI(cfg) : null;
  }

  /** Test connection by fetching repo info. Returns true/false. */
  async testConnection() {
    const { owner, repo } = this.config;
    const res = await fetch(`${GH_API}/repos/${owner}/${repo}`, {
      headers: this.headers
    });
    return res.ok;
  }
}
