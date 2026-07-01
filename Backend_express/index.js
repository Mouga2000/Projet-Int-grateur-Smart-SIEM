// =============================================================================
// Smart SIEM — Mock Backend Node.js
// Un seul fichier | Express + fausse BD db.json
//
// Install : npm install express jsonwebtoken bcryptjs cors uuid speakeasy qrcode
// Run     : node index.js
// Swagger  : http://localhost:8000/api-docs (si tu veux ajouter swagger-ui-express)
// =============================================================================

const express    = require("express");
const jwt        = require("jsonwebtoken");
const bcrypt     = require("bcryptjs");
const cors       = require("cors");
const { v4: uuidv4 } = require("uuid");
const speakeasy  = require("speakeasy");
const QRCode     = require("qrcode");
const fs         = require("fs");
const path       = require("path");
const crypto     = require("crypto");

// =============================================================================
// CONFIG
// =============================================================================

const PORT       = 8000;
const SECRET_KEY = "smart-siem-mock-secret-change-in-production";
const DB_PATH    = path.join(__dirname, "db.json");
const TOKEN_EXPIRES = "8h";

const app = express();
app.use(express.json());
app.use(cors({ origin: "*", credentials: true }));

// =============================================================================
// DB HELPERS — lecture/écriture db.json
// =============================================================================

function readDB() {
  return JSON.parse(fs.readFileSync(DB_PATH, "utf-8"));
}

function writeDB(data) {
  fs.writeFileSync(DB_PATH, JSON.stringify(data, null, 2), "utf-8");
}

function nextId(db, entity) {
  const id = db.id_sequences[entity];
  db.id_sequences[entity] += 1;
  return id;
}

function audit(db, userId, username, action, resource, ip = "127.0.0.1") {
  db.audit_logs.push({
    id: nextId(db, "audit_logs"),
    user_id: userId,
    username,
    action,
    resource,
    ip,
    timestamp: new Date().toISOString(),
  });
}

// =============================================================================
// SEED LOGS au démarrage si la liste est vide
// =============================================================================

function seedLogs() {
  const db = readDB();
  if (db.logs.length > 0) return;

  const severities = ["debug", "info", "info", "info", "warning", "warning", "error", "critical"];
  const logTypes   = ["auth", "reseau", "systeme", "application"];
  const hosts      = ["srv-web-01", "srv-db-01", "fw-01", "proxy-01", "dc-01"];
  const tags_pool  = ["firewall","ssh","auth","web","database","network","system","scan","brute-force"];
  const messages   = [
    (a, b) => `Failed password for root from 192.168.1.${a} port ${b}`,
    (a, b) => `Accepted publickey for admin from 10.0.0.${a} port ${b}`,
    (a, b) => `Connection refused from 172.16.${a}.${b} to port 22`,
    (a)    => `SQL injection attempt detected from 203.0.113.${a}`,
    (a, b) => `Port scan detected: ${a} ports in 10s from 198.51.100.${b}`,
    (a, b) => `Brute force attack: ${a} attempts from 192.168.0.${b}`,
    ()     => `File permission changed on /etc/passwd by user root`,
    (a)    => `SSH session opened for user admin from 10.10.0.${a}`,
    (a, b) => `Firewall blocked connection from 203.0.${a}.${b} to port 443`,
    (a)    => `CPU usage spike: ${a}% detected`,
    (a)    => `Disk space critical: ${a}% used on /var`,
    ()     => `Service nginx restarted after crash`,
    ()     => `New device connected to network`,
    (a)    => `User admin logged out after ${a} minutes of inactivity`,
  ];

  const rand = (n) => Math.floor(Math.random() * n);
  const randInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;
  const randIp  = () => `${randInt(1,254)}.${randInt(0,254)}.${randInt(0,254)}.${randInt(1,254)}`;
  const randMsg = () => {
    const fn = messages[rand(messages.length)];
    return fn(randInt(1,254), randInt(1024, 65535));
  };
  const sample = (arr, n) => [...arr].sort(() => 0.5 - Math.random()).slice(0, n);

  const logs = [];
  for (let i = 0; i < 200; i++) {
    const deltaMs = randInt(0, 30 * 24 * 60 * 60 * 1000);
    const ts = new Date(Date.now() - deltaMs).toISOString();
    logs.push({
      id: uuidv4(),
      timestamp: ts,
      source_ip: randIp(),
      host: hosts[rand(hosts.length)],
      log_type: logTypes[rand(logTypes.length)],
      severity: severities[rand(severities.length)],
      raw_message: randMsg(),
      tags: sample(tags_pool, randInt(1, 3)),
    });
  }

  db.logs = logs;
  writeDB(db);
  console.log(`✅ ${logs.length} logs générés dans db.json`);
}

seedLogs();

// =============================================================================
// MIDDLEWARES
// =============================================================================

function authenticate(req, res, next) {
  const header = req.headers["authorization"] || "";
  const token  = header.replace("Bearer ", "").trim();
  if (!token) return res.status(401).json({ detail: "Token manquant" });
  try {
    req.user = jwt.verify(token, SECRET_KEY);
    // Recharger l'user depuis la DB pour avoir les infos à jour
    const db = readDB();
    const user = db.users.find((u) => u.id === req.user.user_id);
    if (!user) return res.status(401).json({ detail: "Utilisateur non trouvé" });
    req.userFull = user;
    next();
  } catch {
    return res.status(401).json({ detail: "Token invalide ou expiré" });
  }
}

function requireRole(...roles) {
  return [
    authenticate,
    (req, res, next) => {
      if (!roles.includes(req.userFull.role)) {
        return res.status(403).json({ detail: "Accès non autorisé" });
      }
      next();
    },
  ];
}

function userResponse(user) {
  return {
    id: user.id,
    username: user.username,
    email: user.email,
    role: user.role,
    perimeter: user.perimeter,
    mfa_enabled: user.mfa_enabled,
    created_at: user.created_at,
    last_login: user.last_login,
  };
}

function logResponse(log) {
  return {
    id: log.id,
    timestamp: log.timestamp,
    source_ip: log.source_ip,
    host: log.host,
    log_type: log.log_type || null,
    severity: log.severity,
    raw_message: log.raw_message,
    tags: log.tags || [],
  };
}

function paginate(items, page, size) {
  const total = items.length;
  const start = (page - 1) * size;
  return {
    items: items.slice(start, start + size),
    total,
    page,
    size,
    pages: Math.max(1, Math.ceil(total / size)),
  };
}

// =============================================================================
// AUTH — /api/v1/auth
// =============================================================================

const authRouter = express.Router();

// POST /login
authRouter.post("/login", async (req, res) => {
  const { username, password, mfa_code } = req.body;
  const db   = readDB();
  const user = db.users.find((u) => u.username === username);

  if (!user || user.password !== password) {
    return res.status(401).json({ detail: "Identifiants incorrects" });
  }

  // Vérification MFA
  if (user.mfa_enabled) {
    if (!mfa_code) {
      return res.status(401).json({ detail: "MFA requis : veuillez fournir votre code TOTP" });
    }
    const valid = speakeasy.totp.verify({
      secret: user.mfa_secret,
      encoding: "base32",
      token: mfa_code,
      window: 1,
    });
    if (!valid) {
      return res.status(401).json({ detail: "Code MFA invalide" });
    }
  }

  // Mise à jour last_login
  user.last_login = new Date().toISOString();
  audit(db, user.id, user.username, "LOGIN", "auth", req.ip);
  writeDB(db);

  const token = jwt.sign(
    { sub: user.username, role: user.role, user_id: user.id },
    SECRET_KEY,
    { expiresIn: TOKEN_EXPIRES }
  );

  return res.json({
    access_token: token,
    refresh_token: null,
    token_type: "bearer",
    expires_in: 8 * 3600,
    user: userResponse(user),
  });
});

// POST /logout
authRouter.post("/logout", authenticate, (req, res) => {
  const db = readDB();
  audit(db, req.userFull.id, req.userFull.username, "LOGOUT", "auth", req.ip);
  writeDB(db);
  return res.json({ message: "Déconnexion réussie" });
});

// GET /mfa/status
authRouter.get("/mfa/status", authenticate, (req, res) => {
  return res.json({ mfa_enabled: req.userFull.mfa_enabled });
});

// POST /mfa/setup
authRouter.post("/mfa/setup", authenticate, async (req, res) => {
  const secret = speakeasy.generateSecret({
    name: `Smart SIEM (${req.userFull.username})`,
    length: 20,
  });

  const db   = readDB();
  const user = db.users.find((u) => u.id === req.userFull.id);
  user.mfa_secret = secret.base32;
  writeDB(db);

  const qr_code = await QRCode.toDataURL(secret.otpauth_url);
  // Retourner juste le base64 sans le préfixe data:image/png;base64,
  const qr_base64 = qr_code.replace(/^data:image\/png;base64,/, "");

  return res.json({
    secret: secret.base32,
    uri: secret.otpauth_url,
    qr_code: qr_base64,
  });
});

// POST /mfa/verify
authRouter.post("/mfa/verify", authenticate, (req, res) => {
  const { code } = req.body;
  const db   = readDB();
  const user = db.users.find((u) => u.id === req.userFull.id);

  if (!user.mfa_secret) {
    return res.status(400).json({ detail: "Aucun secret MFA. Faites d'abord /mfa/setup" });
  }

  const valid = speakeasy.totp.verify({
    secret: user.mfa_secret,
    encoding: "base32",
    token: code,
    window: 1,
  });

  if (!valid) return res.status(400).json({ detail: "Code MFA invalide" });

  user.mfa_enabled = true;
  writeDB(db);
  return res.json({ mfa_enabled: true });
});

// POST /mfa/disable
authRouter.post("/mfa/disable", authenticate, (req, res) => {
  const { current_password } = req.body;
  const db   = readDB();
  const user = db.users.find((u) => u.id === req.userFull.id);

  if (user.password !== current_password) {
    return res.status(400).json({ detail: "Mot de passe incorrect" });
  }

  user.mfa_enabled = false;
  user.mfa_secret  = null;
  writeDB(db);
  return res.json({ mfa_enabled: false });
});

// =============================================================================
// USERS — /api/v1/users
// =============================================================================

const usersRouter = express.Router();

// GET /
usersRouter.get("/", ...requireRole("administrateur"), (req, res) => {
  const db = readDB();
  return res.json(db.users.map(userResponse));
});

// GET /me
usersRouter.get("/me", authenticate, (req, res) => {
  return res.json(userResponse(req.userFull));
});

// POST /setup
usersRouter.post("/setup", (req, res) => {
  const db = readDB();
  const admins = db.users.filter((u) => u.role === "administrateur");
  if (admins.length > 0) {
    return res.status(403).json({ detail: "Un administrateur existe déjà" });
  }
  const { username, email, password, perimeter = [] } = req.body;
  if (db.users.find((u) => u.username === username)) {
    return res.status(400).json({ detail: "Nom d'utilisateur déjà pris" });
  }
  const newUser = {
    id: nextId(db, "users"),
    username, email, password,
    role: "administrateur",
    perimeter,
    mfa_enabled: false,
    mfa_secret: null,
    created_at: new Date().toISOString(),
    last_login: null,
  };
  db.users.push(newUser);
  writeDB(db);
  return res.json(userResponse(newUser));
});

// POST /
usersRouter.post("/", ...requireRole("administrateur"), (req, res) => {
  const db = readDB();
  const { username, email, password, role = "lecteur", perimeter = [] } = req.body;

  if (db.users.find((u) => u.username === username)) {
    return res.status(400).json({ detail: "Nom d'utilisateur déjà pris" });
  }

  const newUser = {
    id: nextId(db, "users"),
    username, email, password, role, perimeter,
    mfa_enabled: false,
    mfa_secret: null,
    created_at: new Date().toISOString(),
    last_login: null,
  };
  db.users.push(newUser);
  audit(db, req.userFull.id, req.userFull.username, "CREATE_USER", `users/${newUser.id}`, req.ip);
  writeDB(db);
  return res.status(201).json(userResponse(newUser));
});

// PUT /:username/role
usersRouter.put("/:username/role", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const user = db.users.find((u) => u.username === req.params.username);
  if (!user) return res.status(404).json({ detail: "Utilisateur non trouvé" });
  user.role = req.body.role;
  audit(db, req.userFull.id, req.userFull.username, "UPDATE_ROLE", `users/${user.id}`, req.ip);
  writeDB(db);
  return res.json(userResponse(user));
});

// PUT /:username/perimeter
usersRouter.put("/:username/perimeter", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const user = db.users.find((u) => u.username === req.params.username);
  if (!user) return res.status(404).json({ detail: "Utilisateur non trouvé" });
  user.perimeter = req.body.perimeter || [];
  writeDB(db);
  return res.json(userResponse(user));
});

// =============================================================================
// LOGS — /api/v1/logs
// =============================================================================

const logsRouter = express.Router();

// GET /
logsRouter.get("/", authenticate, (req, res) => {
  const db   = readDB();
  const page = parseInt(req.query.page) || 1;
  const size = parseInt(req.query.size) || 50;
  const sorted = [...db.logs].sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  return res.json(paginate(sorted.map(logResponse), page, size));
});

// POST /search
logsRouter.post("/search", authenticate, (req, res) => {
  const db   = readDB();
  const page = parseInt(req.body.page) || 1;
  const size = parseInt(req.body.size) || 50;
  const {
    query, source_ips, hosts, log_types,
    severities, tags, date_from, date_to,
  } = req.body;

  let logs = [...db.logs];

  if (query && query !== "*") {
    const q = query.toLowerCase();
    logs = logs.filter((l) => l.raw_message.toLowerCase().includes(q));
  }
  if (source_ips?.length)  logs = logs.filter((l) => source_ips.includes(l.source_ip));
  if (hosts?.length)       logs = logs.filter((l) => hosts.includes(l.host));
  if (log_types?.length)   logs = logs.filter((l) => log_types.includes(l.log_type));
  if (severities?.length)  logs = logs.filter((l) => severities.includes(l.severity));
  if (tags?.length)        logs = logs.filter((l) => l.tags?.some((t) => tags.includes(t)));
  if (date_from)           logs = logs.filter((l) => l.timestamp >= date_from);
  if (date_to)             logs = logs.filter((l) => l.timestamp <= date_to);

  logs.sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  return res.json(paginate(logs.map(logResponse), page, size));
});

// GET /timeline
logsRouter.get("/timeline", authenticate, (req, res) => {
  const db         = readDB();
  const { interval = "1h", date_from, date_to, severities } = req.query;

  let logs = [...db.logs];
  if (date_from) logs = logs.filter((l) => l.timestamp >= date_from);
  if (date_to)   logs = logs.filter((l) => l.timestamp <= date_to);
  if (severities) {
    const sevList = severities.split(",");
    logs = logs.filter((l) => sevList.includes(l.severity));
  }

  // Grouper par heure
  const buckets = {};
  for (const l of logs) {
    const key = l.timestamp.slice(0, 13) + ":00:00.000Z";
    buckets[key] = (buckets[key] || 0) + 1;
  }
  const timeline = Object.entries(buckets)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([timestamp, count]) => ({ timestamp, count }));

  return res.json({
    timeline,
    total: logs.length,
    interval,
    bucket_count: timeline.length,
  });
});

// POST /ingest
logsRouter.post("/ingest", (req, res) => {
  const raw = req.body;
  const db  = readDB();
  const log = {
    id: uuidv4(),
    timestamp: raw.timestamp || new Date().toISOString(),
    source_ip: raw.source_ip || raw.src_ip || "0.0.0.0",
    host: raw.host || raw.hostname || "unknown",
    log_type: raw.log_type || raw.type || "systeme",
    severity: raw.severity || raw.level || "info",
    raw_message: raw.raw_message || raw.message || JSON.stringify(raw),
    tags: raw.tags || [],
  };
  db.logs.push(log);
  writeDB(db);
  return res.status(201).json(logResponse(log));
});

// GET /:id
logsRouter.get("/:id", authenticate, (req, res) => {
  const db  = readDB();
  const log = db.logs.find((l) => l.id === req.params.id);
  if (!log) return res.status(404).json({ detail: "Log non trouvé" });
  return res.json(logResponse(log));
});

// DELETE /:id
logsRouter.delete("/:id", authenticate, (req, res) => {
  const db  = readDB();
  const idx = db.logs.findIndex((l) => l.id === req.params.id);
  if (idx === -1) return res.status(404).json({ detail: "Log non trouvé" });
  db.logs.splice(idx, 1);
  writeDB(db);
  return res.status(204).send();
});

// =============================================================================
// INVESTIGATIONS — /api/v1/investigations
// =============================================================================

const invRouter = express.Router();

// POST /
invRouter.post("/", ...requireRole("analyste", "administrateur"), (req, res) => {
  const db  = readDB();
  const now = new Date().toISOString();
  const { title, description, severity = "medium", tags = [], log_ids = [], mitre_tactic, mitre_technique } = req.body;

  const inv = {
    id: nextId(db, "investigations"),
    title, description, severity,
    status: "ouverte",
    tags, mitre_tactic, mitre_technique,
    created_by: req.userFull.id,
    assigned_to: null,
    created_at: now,
    updated_at: now,
    logs: log_ids
      .map((lid) => db.logs.find((l) => l.id === lid))
      .filter(Boolean)
      .map((l) => ({ ...logResponse(l), note: null, verdict: "suspect" })),
  };

  db.investigations.push(inv);
  audit(db, req.userFull.id, req.userFull.username, "CREATE_INVESTIGATION", `investigations/${inv.id}`, req.ip);
  writeDB(db);
  return res.status(201).json(inv);
});

// GET /
invRouter.get("/", authenticate, (req, res) => {
  const db     = readDB();
  const page   = parseInt(req.query.page) || 1;
  const size   = parseInt(req.query.size) || 50;
  const status = req.query.status;

  let items = [...db.investigations];
  if (status) items = items.filter((i) => i.status === status);
  items.sort((a, b) => b.created_at.localeCompare(a.created_at));

  // Ne pas retourner les logs dans la liste (trop lourd)
  const light = items.map(({ logs, ...rest }) => rest);
  return res.json(paginate(light, page, size));
});

// GET /:id
invRouter.get("/:id", authenticate, (req, res) => {
  const db  = readDB();
  const inv = db.investigations.find((i) => i.id === parseInt(req.params.id));
  if (!inv) return res.status(404).json({ detail: "Investigation non trouvée" });
  return res.json(inv);
});

// POST /:id/logs
invRouter.post("/:id/logs", ...requireRole("analyste", "administrateur"), (req, res) => {
  const db  = readDB();
  const inv = db.investigations.find((i) => i.id === parseInt(req.params.id));
  if (!inv) return res.status(404).json({ detail: "Investigation non trouvée" });

  const { log_id, note, verdict = "suspect" } = req.body;
  const log = db.logs.find((l) => l.id === log_id);
  if (!log) return res.status(404).json({ detail: "Log non trouvé" });

  const entry = {
    ...logResponse(log),
    note,
    verdict,
    added_by: req.userFull.id,
    added_at: new Date().toISOString(),
  };
  inv.logs.push(entry);
  inv.updated_at = new Date().toISOString();
  writeDB(db);
  return res.status(201).json(entry);
});

// PATCH /:id/status
invRouter.patch("/:id/status", ...requireRole("analyste", "administrateur"), (req, res) => {
  const db  = readDB();
  const inv = db.investigations.find((i) => i.id === parseInt(req.params.id));
  if (!inv) return res.status(404).json({ detail: "Investigation non trouvée" });

  const { status, notes } = req.query;
  inv.status     = status;
  inv.updated_at = new Date().toISOString();
  writeDB(db);
  return res.json({ message: `Statut mis à jour : ${status}` });
});

// PATCH /:id
invRouter.patch("/:id", ...requireRole("analyste", "administrateur"), (req, res) => {
  const db  = readDB();
  const inv = db.investigations.find((i) => i.id === parseInt(req.params.id));
  if (!inv) return res.status(404).json({ detail: "Investigation non trouvée" });

  const allowed = ["title", "description", "severity", "tags", "assigned_to", "mitre_tactic", "mitre_technique"];
  for (const key of allowed) {
    if (req.body[key] !== undefined) inv[key] = req.body[key];
  }
  inv.updated_at = new Date().toISOString();
  writeDB(db);
  return res.json(inv);
});

// =============================================================================
// ADMIN — /api/v1/admin
// =============================================================================

const adminRouter = express.Router();

// POST /purge/logs
adminRouter.post("/purge/logs", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const days = parseInt(req.query.days) || 90;
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const before = db.logs.length;
  db.logs = db.logs.filter((l) => l.timestamp >= cutoff);
  const deleted = before - db.logs.length;
  audit(db, req.userFull.id, req.userFull.username, "PURGE_LOGS", "logs", req.ip);
  writeDB(db);
  return res.json({ deleted, retention_days: days, message: `${deleted} logs supprimés (>${days} jours)` });
});

// POST /purge/audit
adminRouter.post("/purge/audit", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const days = parseInt(req.query.days) || 365;
  const cutoff = new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString();
  const before = db.audit_logs.length;
  db.audit_logs = db.audit_logs.filter((l) => l.timestamp >= cutoff);
  const deleted = before - db.audit_logs.length;
  writeDB(db);
  return res.json({ deleted, retention_days: days, message: `${deleted} audits supprimés (>${days} jours)` });
});

// GET /retention
adminRouter.get("/retention", ...requireRole("administrateur"), (req, res) => {
  return res.json({
    log_retention_days: 90,
    audit_retention_days: 365,
    next_purge: "Tous les jours à 3h00",
  });
});

// =============================================================================
// ARCHIVE — /api/v1/admin/archive
// =============================================================================

const archiveRouter = express.Router();

// POST /create
archiveRouter.post("/create", ...requireRole("administrateur"), (req, res) => {
  const db          = readDB();
  const days        = parseInt(req.query.days) || 90;
  const window_days = parseInt(req.query.window_days) || 30;
  const now         = new Date();
  const date_to     = new Date(now - days * 24 * 60 * 60 * 1000);
  const date_from   = new Date(date_to - window_days * 24 * 60 * 60 * 1000);

  const logsInWindow = db.logs.filter(
    (l) => l.timestamp >= date_from.toISOString() && l.timestamp <= date_to.toISOString()
  );

  if (logsInWindow.length === 0) {
    return res.status(400).json({ detail: "Aucun log dans cette fenêtre temporelle" });
  }

  const lastArchive   = db.archives.length > 0 ? db.archives[db.archives.length - 1] : null;
  const previous_hash = lastArchive ? lastArchive.chain_hash : null;
  const content       = logsInWindow.map((l) => l.id).sort().join("|");
  const chain_hash    = crypto.createHash("sha256")
    .update(`${previous_hash || "GENESIS"}:${content}`)
    .digest("hex");

  const archive = {
    id: nextId(db, "archives"),
    date_from: date_from.toISOString(),
    date_to: date_to.toISOString(),
    log_count: logsInWindow.length,
    chain_hash,
    previous_hash,
    status: "certified",
    certified_at: now.toISOString(),
  };

  db.archives.push(archive);
  audit(db, req.userFull.id, req.userFull.username, "CREATE_ARCHIVE", `archive/${archive.id}`, req.ip);
  writeDB(db);
  return res.status(201).json(archive);
});

// GET /list
archiveRouter.get("/list", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const page = parseInt(req.query.page) || 1;
  const size = parseInt(req.query.size) || 50;
  const sorted = [...db.archives].sort((a, b) => b.certified_at.localeCompare(a.certified_at));
  return res.json(paginate(sorted, page, size));
});

// GET /chain
archiveRouter.get("/chain", ...requireRole("administrateur"), (req, res) => {
  const db   = readDB();
  const chain = db.archives.map((a) => ({
    id: a.id,
    period: `${a.date_from.slice(0, 10)} -> ${a.date_to.slice(0, 10)}`,
    logs: a.log_count,
    chain_hash: a.chain_hash.slice(0, 20) + "...",
    previous_hash: a.previous_hash ? a.previous_hash.slice(0, 20) + "..." : "GENESIS",
    status: a.status,
    certified_at: a.certified_at,
  }));

  return res.json({
    chain,
    length: chain.length,
    integrity: chain.length > 0 ? "verified" : "empty",
  });
});

// POST /verify/:id
archiveRouter.post("/verify/:id", ...requireRole("administrateur"), (req, res) => {
  const db      = readDB();
  const archive = db.archives.find((a) => a.id === parseInt(req.params.id));
  if (!archive) return res.status(404).json({ detail: "Archive non trouvée" });

  // Sur le mock on considère toujours valide sauf si déjà compromised
  const is_valid  = archive.status !== "compromised";
  archive.status  = is_valid ? "verified" : "compromised";
  writeDB(db);

  return res.json({
    valid: is_valid,
    details: {
      chain_hash: archive.chain_hash,
      previous_hash: archive.previous_hash,
      status: archive.status,
      log_count: archive.log_count,
    },
  });
});

// GET /:id
archiveRouter.get("/:id", ...requireRole("administrateur"), (req, res) => {
  const db      = readDB();
  const archive = db.archives.find((a) => a.id === parseInt(req.params.id));
  if (!archive) return res.status(404).json({ detail: "Archive non trouvée" });
  return res.json(archive);
});

// GET /:id/export
archiveRouter.get("/:id/export", ...requireRole("administrateur"), (req, res) => {
  const db      = readDB();
  const archive = db.archives.find((a) => a.id === parseInt(req.params.id));
  if (!archive) return res.status(404).json({ detail: "Archive non trouvée" });

  return res.json({
    archive_id: archive.id,
    exported_at: new Date().toISOString(),
    exported_by: req.userFull.username,
    chain_hash: archive.chain_hash,
    previous_hash: archive.previous_hash,
    log_count: archive.log_count,
    period: `${archive.date_from.slice(0, 10)} -> ${archive.date_to.slice(0, 10)}`,
    status: archive.status,
    certified_at: archive.certified_at,
    integrity_proof: crypto.createHash("sha256").update(archive.chain_hash).digest("hex"),
  });
});

// =============================================================================
// HEALTH
// =============================================================================

app.get("/api/v1/health", (req, res) => {
  const db = readDB();
  return res.json({
    status: "ok",
    mode: "mock-js",
    timestamp: new Date().toISOString(),
    stats: {
      users: db.users.length,
      logs: db.logs.length,
      investigations: db.investigations.length,
      archives: db.archives.length,
    },
  });
});

// =============================================================================
// MONTAGE DES ROUTERS
// =============================================================================

app.use("/api/v1/auth",               authRouter);
app.use("/api/v1/users",              usersRouter);
app.use("/api/v1/logs",               logsRouter);
app.use("/api/v1/investigations",     invRouter);
app.use("/api/v1/admin/archive",      archiveRouter);
app.use("/api/v1/admin",              adminRouter);

// =============================================================================
// START
// =============================================================================

app.listen(PORT, () => {
  console.log(`\n🚀 Smart SIEM Mock Backend démarré`);
  console.log(`   URL     : http://localhost:${PORT}`);
  console.log(`   Health  : http://localhost:${PORT}/api/v1/health`);
  console.log(`\n📋 Comptes de démonstration :`);
  console.log(`   admin      / Admin123!    (administrateur)`);
  console.log(`   analyste1  / Analyste1!   (analyste)`);
  console.log(`   rssi1      / Rssi1234!    (rssi)`);
  console.log(`   auditeur1  / Auditeur1!   (auditeur)`);
  console.log(`   lecteur1   / Lecteur1!    (lecteur)`);
  console.log(`\n📁 Base de données : db.json\n`);
});