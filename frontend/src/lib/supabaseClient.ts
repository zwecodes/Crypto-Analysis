import { createClient } from "@supabase/supabase-js";
import { env } from "../config/env";

/**
 * Single shared Supabase client for the whole app.
 * Auth (sign up, login, session) is handled entirely on the client via this
 * instance, per docs/api-contract.md — there are no custom backend auth
 * endpoints. The backend only validates the JWT this client produces.
 */
export const supabase = createClient(
  env.supabaseUrl,
  env.supabasePublishableKey
);
