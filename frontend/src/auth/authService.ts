import { supabase } from "../lib/supabaseClient";
import type { AuthError, Session, User } from "@supabase/supabase-js";

/**
 * Thin wrapper around Supabase Auth calls. Components should call these
 * functions rather than importing `supabase` directly, so all auth logic
 * stays in one place. No passwords are ever stored or logged here — they
 * are passed straight through to Supabase over HTTPS.
 */

export interface SignUpResult {
  user: User | null;
  session: Session | null;
  /** True when Supabase requires email confirmation before the session is active. */
  requiresEmailConfirmation: boolean;
}

export async function signUp(
  email: string,
  password: string
): Promise<SignUpResult> {
  const { data, error } = await supabase.auth.signUp({ email, password });

  if (error) {
    throw error;
  }

  // When email confirmation is required, Supabase returns a user but no
  // active session yet — that's how we detect this case without assuming
  // the project's Supabase Auth settings.
  const requiresEmailConfirmation = data.user !== null && data.session === null;

  return {
    user: data.user,
    session: data.session,
    requiresEmailConfirmation,
  };
}

export async function login(email: string, password: string): Promise<Session> {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    throw error;
  }

  if (!data.session) {
    // Defensive: signInWithPassword should always return a session on success.
    throw new Error("Login succeeded but no session was returned.");
  }

  return data.session;
}

export async function logout(): Promise<void> {
  const { error } = await supabase.auth.signOut();

  if (error) {
    throw error;
  }
}

/** Maps a Supabase AuthError (or unknown thrown value) to a readable message. */
export function getAuthErrorMessage(error: unknown): string {
  if (isAuthError(error)) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong. Please try again.";
}

function isAuthError(error: unknown): error is AuthError {
  return (
    typeof error === "object" &&
    error !== null &&
    "message" in error &&
    "status" in error
  );
}