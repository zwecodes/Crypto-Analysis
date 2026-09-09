import { Link } from "react-router-dom";
import "./NotFoundPage.css";

export function NotFoundPage() {
  return (
    <div className="not-found-page">
      <h1>404</h1>
      <p>Page not found.</p>
      <Link to="/dashboard">Back to Dashboard</Link>
    </div>
  );
}
