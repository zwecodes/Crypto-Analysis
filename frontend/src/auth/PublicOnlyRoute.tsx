import { Navigate } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "./useAuth";
import { Spinner } from "../components/ui/Spinner";

interface PublicOnlyRouteProps {
  children: ReactNode;
}

/**
 * Wrap /login and /signup. If the user is already authenticated, sends them
 * to /dashboard instead of showing the auth form again. Waits for the
 * initial session check first, same as ProtectedRoute, to avoid a flash.
 */
export function PublicOnlyRoute({ children }: PublicOnlyRouteProps) {
  const { user, loading } = useAuth();

  if (loading) {
    return <Spinner label="Checking session..." />;
  }

  if (user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}