// src/config/roles.ts

export const Role = {
  LECTEUR: "lecteur",
  ANALYSTE: "analyste",
  AUDITEUR: "auditeur",
  RSSI: "rssi",
  ADMINISTRATEUR: "administrateur",
} as const;

export type Role = typeof Role[keyof typeof Role];

export const PAGE_ROLES: Record<string, Role[]> = {
  dashboard:      [Role.ANALYSTE, Role.RSSI, Role.LECTEUR, Role.ADMINISTRATEUR],
  investigations: [Role.ANALYSTE, Role.ADMINISTRATEUR],
  logs:           [Role.ANALYSTE, Role.ADMINISTRATEUR, Role.LECTEUR],
  adminUsers:     [Role.ADMINISTRATEUR],
  adminPurge:     [Role.ADMINISTRATEUR],
  archive:        [Role.ADMINISTRATEUR],
  profile:        [Role.LECTEUR, Role.ANALYSTE, Role.AUDITEUR, Role.RSSI, Role.ADMINISTRATEUR],
};

export const hasAccess = (page: string, userRole: Role): boolean =>
  PAGE_ROLES[page]?.includes(userRole) ?? false;