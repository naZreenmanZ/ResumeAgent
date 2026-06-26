import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function DashboardPage() {
  return (
    <PlaceholderPage
      eyebrow="Dashboard"
      title="A calm command center for each job search run."
      description="This shell will summarize scans, queued jobs, resume approvals, applications, duplicate states, and portal warnings once the backend API is added."
      status="Shell only: no live data connected"
      primaryAction="Run scan now"
      secondaryAction="Review queue"
      emptyTitle="No run data yet"
      emptyBody="Issue 1 creates the workspace shell. Live scan summaries arrive in later issues when the backend API is connected."
      panels={[
        {
          title: "Today",
          body: "Prepared for future run metrics without hardcoded personal history.",
          items: ["Jobs found", "Queued roles", "Portal warnings"],
        },
        {
          title: "Approval First",
          body: "The interface keeps upload and submit actions visible and controlled.",
          items: ["Resume review", "PDF approval", "Final submit approval"],
        },
        {
          title: "Local Privacy",
          body: "The shell avoids personal resume content and tracker records.",
          items: ["Ignored config", "Ignored resumes", "Ignored trackers"],
        },
      ]}
    />
  );
}
