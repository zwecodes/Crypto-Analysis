import "./PagePlaceholder.css";

interface PagePlaceholderProps {
  title: string;
  description?: string;
}

/**
 * Generic "coming soon" placeholder. Used by every feature page until its
 * real implementation milestone. Not part of the originally listed
 * component set — added to avoid duplicating the same markup across six
 * placeholder pages.
 */
export function PagePlaceholder({ title, description }: PagePlaceholderProps) {
  return (
    <div className="page-placeholder">
      <h1>{title}</h1>
      <p>{description ?? "This page is not implemented yet."}</p>
    </div>
  );
}
