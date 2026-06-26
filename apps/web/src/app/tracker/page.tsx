import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function TrackerPage() {
  return (
    <PlaceholderPage
      eyebrow="Tracker"
      title="Keep application history readable and exportable."
      description="The tracker view is prepared for application dates, portal references, resume paths, statuses, and CSV/XLSX export controls."
      status="No tracker rows connected"
      primaryAction="Export CSV"
      secondaryAction="Export XLSX"
      emptyTitle="No applications tracked in the UI yet"
      emptyBody="Existing local tracker files stay private. Later issues will connect local application records to this table."
      tableLabels={["Applied", "Portal", "Company", "Status"]}
      panels={[
        {
          title: "Spreadsheet Feel",
          body: "Tracker interactions should remain dense, sortable, and easy to scan.",
        },
        {
          title: "Private Paths",
          body: "Resume PDF paths will be visible only from local state, never hardcoded.",
        },
        {
          title: "Status History",
          body: "Applied, already applied, skipped, and failed states will stay explicit.",
        },
      ]}
    />
  );
}
