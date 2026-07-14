// src/config/endpoints.ts
//
// ATTENTION : chemins relatifs uniquement !
// Le baseURL est déjà défini dans api.ts (VITE_API_BASE_URL).
// Si tu mets le préfixe ici, Axios le double avec baseURL → URL cassée.

export const ENDPOINTS = {
  auth: {
    login:      `/auth/login`,
    logout:     `/auth/logout`,
    mfaStatus:  `/auth/mfa/status`,
    mfaSetup:   `/auth/mfa/setup`,
    mfaVerify:  `/auth/mfa/verify`,
    mfaDisable: `/auth/mfa/disable`,
  },

  users: {
    list:          `/users/`,
    create:        `/users/`,
    setup:         `/users/setup`,
    me:            `/users/me`,
    updateRole:      (username: string) => `/users/${username}/role`,
    updatePerimeter: (username: string) => `/users/${username}/perimeter`,
  },

  logs: {
    ingest:   `/logs/ingest`,
    list:     `/logs/`,
    search:   `/logs/search`,
    timeline: `/logs/timeline`,
    detail:   (id: string) => `/logs/${id}`,
  },

  investigations: {
    list:    `/investigations/`,
    create:  `/investigations/`,
    detail:  (id: number) => `/investigations/${id}`,
    addLog:  (id: number) => `/investigations/${id}/logs`,
    status:  (id: number) => `/investigations/${id}/status`,
    update:  (id: number) => `/investigations/${id}`,
  },

  admin: {
    purgeLogs:  `/admin/purge/logs`,
    purgeAudit: `/admin/purge/audit`,
    retention:  `/admin/retention`,
  },

  archive: {
    create:  `/admin/archive/create`,
    list:    `/admin/archive/list`,
    chain:   `/admin/archive/chain`,
    verify:  (id: number) => `/admin/archive/verify/${id}`,
    detail:  (id: number) => `/admin/archive/${id}`,
    export:  (id: number) => `/admin/archive/${id}/export`,
  },

  audit: {
    logs: `/audit/logs`,
  },

  rules: {
    list:    `/rules/`,
    create:  `/rules/`,
    update:  (id: string) => `/rules/${id}`,
    delete:  (id: string) => `/rules/${id}`,
  },

  playbooks: {
    list:    `/playbooks/`,
    create:  `/playbooks/`,
    detail:  (id: number) => `/playbooks/${id}`,
    update:  (id: number) => `/playbooks/${id}`,
    delete:  (id: number) => `/playbooks/${id}`,
    execute: (id: number) => `/playbooks/${id}/execute`,
  },
};