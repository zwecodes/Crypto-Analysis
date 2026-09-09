import { createBrowserRouter, Navigate } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { LoginPage } from "./pages/auth/LoginPage";
import { SignupPage } from "./pages/auth/SignupPage";
import { DashboardPage } from "./pages/dashboard/DashboardPage";
import { StrategyPickerPage } from "./pages/strategies/StrategyPickerPage";
import { BacktestResultsPage } from "./pages/backtest/BacktestResultsPage";
import { AlertSettingsPage } from "./pages/alerts/AlertSettingsPage";
import { NotFoundPage } from "./pages/NotFoundPage";

/**
 * Route table for Milestone 1. Auth pages are standalone (no sidebar/header
 * chrome) since a logged-out user shouldn't see app navigation. Everything
 * else sits inside AppLayout. There is no route guarding yet — real
 * authentication and protected routes are a later milestone.
 */
export const router = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/signup",
    element: <SignupPage />,
  },
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/dashboard" replace /> },
      { path: "dashboard", element: <DashboardPage /> },
      { path: "strategies", element: <StrategyPickerPage /> },
      { path: "backtest", element: <BacktestResultsPage /> },
      { path: "alerts", element: <AlertSettingsPage /> },
    ],
  },
  {
    path: "*",
    element: <NotFoundPage />,
  },
]);
