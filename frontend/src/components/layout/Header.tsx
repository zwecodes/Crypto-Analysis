import { useNavigate } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";
import { logout, getAuthErrorMessage } from "../../auth/authService";
import "./Header.css";

export function Header() {
  const { user } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    try {
      await logout();
      navigate("/login", { replace: true });
    } catch (error) {
      console.error("Logout failed:", getAuthErrorMessage(error));
    }
  }

  return (
    <header className="app-header">
      <span className="app-header-title">Crypto Analysis</span>
      {user && (
        <div className="app-header-user">
          <span className="app-header-email">{user.email}</span>
          <button
            type="button"
            className="app-header-logout"
            onClick={handleLogout}
          >
            Logout
          </button>
        </div>
      )}
    </header>
  );
}
