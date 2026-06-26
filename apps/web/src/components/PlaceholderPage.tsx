type Panel = {
  title: string;
  body: string;
  items?: string[];
};

type PlaceholderPageProps = {
  eyebrow: string;
  title: string;
  description: string;
  status: string;
  primaryAction: string;
  secondaryAction: string;
  emptyTitle: string;
  emptyBody: string;
  panels: Panel[];
  tableLabels?: string[];
};

export function PlaceholderPage({
  eyebrow,
  title,
  description,
  status,
  primaryAction,
  secondaryAction,
  emptyTitle,
  emptyBody,
  panels,
  tableLabels,
}: PlaceholderPageProps) {
  return (
    <section className="page" aria-labelledby="page-title">
      <header className="page-header">
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h1 className="page-title" id="page-title">
            {title}
          </h1>
          <p className="page-description">{description}</p>
        </div>
      </header>

      <div className="status-strip" aria-label="Current section status">
        <span className="status-pill">{status}</span>
        <div className="action-row">
          <span className="button primary" aria-disabled="true">
            {primaryAction}
          </span>
          <span className="button" aria-disabled="true">
            {secondaryAction}
          </span>
        </div>
      </div>

      <div className="empty-state">
        <h2>{emptyTitle}</h2>
        <p>{emptyBody}</p>
      </div>

      {tableLabels ? (
        <div className="placeholder-table" aria-label="Placeholder table">
          <div className="table-row header">
            {tableLabels.map((label) => (
              <span key={label}>{label}</span>
            ))}
          </div>
          {[0, 1, 2].map((row) => (
            <div className="table-row" key={row}>
              {tableLabels.map((label) => (
                <span className="ghost-cell" key={label} aria-hidden="true" />
              ))}
            </div>
          ))}
        </div>
      ) : null}

      <div className="grid">
        {panels.map((panel) => (
          <article className="panel" key={panel.title}>
            <h2>{panel.title}</h2>
            <p>{panel.body}</p>
            {panel.items ? (
              <ul>
                {panel.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
          </article>
        ))}
      </div>
    </section>
  );
}
