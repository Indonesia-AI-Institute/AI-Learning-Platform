/**
 * auth.types.ts
 * =============
 * Type definitions for authentication.
 */

export type UserRole = "student" | "teacher";

export interface User {
  id: string;
  full_name: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  password: string;
  role: UserRole;
}