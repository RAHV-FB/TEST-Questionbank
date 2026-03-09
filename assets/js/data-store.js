/**
 * data-store.js
 * Manages all data operations:
 *  - Reading question CSVs
 *  - Reading/writing changes.json, groups.json, changelog.json
 *
 * Falls back to localStorage when GitHub API is not configured.
 */

const PATHS = {
  manifest: 'data/manifest.json',
  changes:  'data/edits/changes.json',
  groups:   'data/edits/groups.json',
  changelog:'data/edits/changelog.json'
};

const DRAFT_KEY   = 'qb_draft_changes';
const GROUPS_KEY  = 'qb_draft_groups';
const CLKEY       = 'qb_draft_changelog';

class DataStore {
  /**
   * @param {GitHubAPI|null} api - GitHub API instance, or null for local-only mode
   * @param {string} baseURL - Base URL for fetching static assets (e.g. CSV files)
   */
  constructor(api, baseURL) {
    this.api     = api;
    this.baseURL = baseURL.replace(/\/$/, '');
  }

  // -------------------------
  // CSV / Question loading
  // -------------------------

  /** Fetch text from the static site (no auth needed). */
  async _fetchText(path) {
    const url = `${this.baseURL}/${path}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch ${url} (${res.status})`);
    return res.text();
  }

  async _fetchJSON(path) {
    const text = await this._fetchText(path);
    return JSON.parse(text);
  }

  async loadManifest() {
    return this._fetchJSON(PATHS.manifest);
  }

  async loadCSV(filename) {
    const text = await this._fetchText(`data/questions/${filename}`);
    return parseCSV(text);
  }

  // -------------------------
  // Changes
  // -------------------------

  async _getChanges() {
    if (this.api) {
      const result = await this.api.readJSON(PATHS.changes);
      if (result && result.data) return result;
    }
    // Fallback: try static file served by GitHub Pages
    try {
      const data = await this._fetchJSON(PATHS.changes);
      if (data && typeof data === 'object') return { data, sha: null };
    } catch { /* not yet deployed or unavailable */ }
    // Last resort: localStorage
    try {
      const raw = localStorage.getItem(DRAFT_KEY);
      const data = raw ? JSON.parse(raw) : { schema_version:'1.0', last_updated:null, changes:{} };
      return { data, sha: null };
    } catch { return { data:{ schema_version:'1.0', last_updated:null, changes:{} }, sha:null }; }
  }

  async getChanges() {
    const result = await this._getChanges();
    return result.data.changes || {};
  }

  /**
   * Save a single question change.
   * @param {string} id         - questionId()
   * @param {object} changeData - { original, edited, status, needsMoreInfo }
   * @param {string} logMessage - Human-readable description for changelog
   */
  async saveChange(id, changeData, logMessage) {
    const result = await this._getChanges();
    const store  = result.data;

    store.changes[id] = {
      ...changeData,
      timestamp: new Date().toISOString()
    };
    store.last_updated = new Date().toISOString();

    if (this.api) {
      const msg = `edit: ${logMessage} [${id}]`;
      await this.api.writeJSON(PATHS.changes, store, msg, result.sha || null);
    } else {
      localStorage.setItem(DRAFT_KEY, JSON.stringify(store));
    }

    // Always log
    await this._appendLog({
      timestamp: new Date().toISOString(),
      action: 'edit',
      questionId: id,
      description: logMessage,
      before: changeData.original,
      after: changeData.edited
    });
  }

  // -------------------------
  // Groups
  // -------------------------

  async _getGroups() {
    if (this.api) {
      const result = await this.api.readJSON(PATHS.groups);
      if (result && result.data) return result;
    }
    try {
      const data = await this._fetchJSON(PATHS.groups);
      if (data && typeof data === 'object') return { data, sha: null };
    } catch { /* not yet deployed */ }
    try {
      const raw = localStorage.getItem(GROUPS_KEY);
      const data = raw ? JSON.parse(raw) : { schema_version:'1.0', last_updated:null, groups:{} };
      return { data, sha: null };
    } catch { return { data:{ schema_version:'1.0', last_updated:null, groups:{} }, sha:null }; }
  }

  async getGroups() {
    const result = await this._getGroups();
    return result.data.groups || {};
  }

  async saveGroup(group) {
    const result = await this._getGroups();
    const store  = result.data;

    if (!group.id) group.id = 'group_' + Date.now();
    group.created_at = group.created_at || new Date().toISOString();
    store.groups[group.id] = group;
    store.last_updated = new Date().toISOString();

    if (this.api) {
      const msg = `group: create/update group ${group.id} — ${group.title || ''}`;
      await this.api.writeJSON(PATHS.groups, store, msg, result.sha || null);
    } else {
      localStorage.setItem(GROUPS_KEY, JSON.stringify(store));
    }

    await this._appendLog({
      timestamp: new Date().toISOString(),
      action: 'group',
      questionId: group.id,
      description: `Group created/updated: "${group.title}"`,
      before: null,
      after: group
    });

    return group;
  }

  async deleteGroup(groupId) {
    const result = await this._getGroups();
    const store  = result.data;
    const removed = store.groups[groupId];
    delete store.groups[groupId];
    store.last_updated = new Date().toISOString();

    if (this.api) {
      await this.api.writeJSON(PATHS.groups, store, `group: delete ${groupId}`, result.sha || null);
    } else {
      localStorage.setItem(GROUPS_KEY, JSON.stringify(store));
    }

    if (removed) {
      await this._appendLog({
        timestamp: new Date().toISOString(),
        action: 'delete-group',
        questionId: groupId,
        description: `Group deleted: "${removed.title}"`,
        before: removed,
        after: null
      });
    }
  }

  // -------------------------
  // Changelog
  // -------------------------

  async _getChangelog() {
    if (this.api) {
      const result = await this.api.readJSON(PATHS.changelog);
      if (result && result.data) return result;
    }
    try {
      const data = await this._fetchJSON(PATHS.changelog);
      if (data && typeof data === 'object') return { data, sha: null };
    } catch { /* not yet deployed */ }
    try {
      const raw = localStorage.getItem(CLKEY);
      const data = raw ? JSON.parse(raw) : { schema_version:'1.0', entries:[] };
      return { data, sha: null };
    } catch { return { data:{ schema_version:'1.0', entries:[] }, sha:null }; }
  }

  async getChangelog() {
    const result = await this._getChangelog();
    return result.data.entries || [];
  }

  async _appendLog(entry) {
    const result = await this._getChangelog();
    const store  = result.data;
    store.entries.unshift(entry); // newest first

    if (this.api) {
      await this.api.writeJSON(PATHS.changelog, store, `log: ${entry.description}`, result.sha || null);
    } else {
      localStorage.setItem(CLKEY, JSON.stringify(store));
    }
  }

  // -------------------------
  // Utility
  // -------------------------

  get isOnline() { return !!this.api; }
}
