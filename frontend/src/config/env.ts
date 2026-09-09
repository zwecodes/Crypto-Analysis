/**
 * Centralized, typed access to environment variables.
 *
 * Vite only exposes variables prefixed with VITE_ to client code
 * (via import.meta.env). Everything read here MUST already be safe
 * for the browser bundle — never add server-only secrets
 * (SUPABASE_SECRET_KEY, AI_API_KEY, EMAIL_APP_PASSWORD) here.
 */

interface AppEnv {
  supabaseUrl: string;
  supabasePublishableKey: string;
  apiBaseUrl: string;
}

function readEnvVar(key: string, value: string | undefined): string {
  if (!value || value.trim() === "") {
    // Fails fast during development instead of silently calling undefined URLs.
    throw new Error(
      `Missing required environment variable: ${key}. ` +
        `Copy frontend/.env.example to frontend/.env.local and fill in real values.`
    );
  }
  return value;
}

export const env: AppEnv = {
  supabaseUrl: readEnvVar(
    "VITE_SUPABASE_URL",
    import.meta.env.VITE_SUPABASE_URL
  ),
  supabasePublishableKey: readEnvVar(
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY
  ),
  apiBaseUrl: readEnvVar(
    "VITE_API_BASE_URL",
    import.meta.env.VITE_API_BASE_URL
  ),
};
