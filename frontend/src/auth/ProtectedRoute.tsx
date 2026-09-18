import { Navigate, useLocation } from "react-router-dom";
import type { ReactNode } from "react";
import { useAuth } from "./useAuth";
import { Spinner } from "../components/ui/Spinner";

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * Wrap any route element that requires authentication. Renders nothing but
 * a loading spinner until the initial session check completes, so a
 * protected page never briefly flashes before redirecting.
 */
export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Spinner label="Checking session..." />;
  }

  if (!user) {
    // Preserve the intended destination so a future "redirect back after
    // login" enhancement has somewhere to read it from; not used yet.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}