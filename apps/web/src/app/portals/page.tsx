import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function PortalsPage() {
  return (
    <PlaceholderPage
      eyebrow="Portals"
      title="Choose sources without hiding setup work."
      description="Portal setup will show enabled state, adapter type, scan method, last warning, and whether a portal still needs configuration."
      status="Portal config not connected"
      primaryAction="Test scan"
      secondaryAction="Add portal"
      emptyTitle="No portal settings loaded"
      emptyBody="Issue 1 creates the view. Later work will load configured portals from the local backend."
      tableLabels={["Portal", "Enabled", "Adapter", "Last state"]}
      panels={[
        {
          title: "Selectable Sources",
          body: "LinkedIn, Indeed, GulfTalent, NaukriGulf, Bayt, Wellfound, and JobTogether remain configurable.",
        },
        {
          title: "Needs Setup",
          body: "Unsupported adapters should look intentionally pending, not broken.",
        },
        {
          title: "Failure Isolation",
          body: "One portal warning should not collapse the entire scan workflow.",
        },
      ]}
    />
  );
}
