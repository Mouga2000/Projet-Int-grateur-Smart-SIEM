// src/types/user.ts
import { Role } from "../config/roles";

export type Perimeter = "equipe" | "service" | "filiale" | "environnement";

export interface User {
  id: number;
  username: string;
  email: string;
  role: Role;
  perimeter: Perimeter[];
  mfa_enabled: boolean;
  created_at: string;
  last_login?: string | null;
}

export interface AuthUser extends User {
  access_token: string;
  refresh_token?: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    username: string;
    email: string;
    role: string;
    perimeter: string[];
    mfa_enabled: boolean;
  };
}