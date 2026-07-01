// src/config/endpoints.ts

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const ENDPOINTS = {
  auth: {
    login:      `${API_BASE}/auth/login`,
    logout:     `${API_BASE}/auth/logout`,
    mfaStatus:  `${API_BASE}/auth/mfa/status`,
    mfaSetup:   `${API_BASE}/auth/mfa/setup`,
    mfaVerify:  `${API_BASE}/auth/mfa/verify`,
    mfaDisable: `${API_BASE}/auth/mfa/disable`,
  },

  users: {
    list:          `${API_BASE}/users/`,
    create:        `${API_BASE}/users/`,
    setup:         `${API_BASE}/users/setup`,
    me:            `${API_BASE}/users/me`,
    updateRole:      (username: string) => `${API_BASE}/users/${username}/role`,
    updatePerimeter: (username: string) => `${API_BASE}/users/${username}/perimeter`,
  },

  logs: {
    ingest:   `${API_BASE}/logs/ingest`,
    list:     `${API_BASE}/logs/`,
    search:   `${API_BASE}/logs/search`,
    timeline: `${API_BASE}/logs/timeline`,
    detail:   (id: string) => `${API_BASE}/logs/${id}`,
  },

  investigations: {
    list:    `${API_BASE}/investigations/`,
    create:  `${API_BASE}/investigations/`,
    detail:  (id: number) => `${API_BASE}/investigations/${id}`,
    addLog:  (id: number) => `${API_BASE}/investigations/${id}/logs`,
    status:  (id: number) => `${API_BASE}/investigations/${id}/status`,
    update:  (id: number) => `${API_BASE}/investigations/${id}`,
  },

  admin: {
    purgeLogs:  `${API_BASE}/admin/purge/logs`,
    purgeAudit: `${API_BASE}/admin/purge/audit`,
    retention:  `${API_BASE}/admin/retention`,
  },

  archive: {
    create:  `${API_BASE}/admin/archive/create`,
    list:    `${API_BASE}/admin/archive/list`,
    chain:   `${API_BASE}/admin/archive/chain`,
    verify:  (id: number) => `${API_BASE}/admin/archive/verify/${id}`,
    detail:  (id: number) => `${API_BASE}/admin/archive/${id}`,
    export:  (id: number) => `${API_BASE}/admin/archive/${id}/export`,
  },
};