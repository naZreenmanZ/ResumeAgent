import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function QueuePage() {
  return (
    <PlaceholderPage
      eyebrow="Job Queue"
      title="Review roles before the agent tailors anything."
      description="The queue view is reserved for relevant jobs, score explanations, duplicate state, portal, region, and selected base resume type."
      status="Waiting for backend queue data"
      primaryAction="Tailor selected"
      secondaryAction="Skip role"
      emptyTitle="No queued jobs yet"
      emptyBody="After scan integration, this screen will show jobs that passed scoring and duplicate checks."
      tableLabels={["Role", "Company", "Portal", "Status"]}
      panels={[
        {
          title: "Fast Scanning",
          body: "The layout favors table-style review over decorative cards.",
        },
        {
          title: "Duplicate Safety",
          body: "Already-applied or duplicate roles will be called out before any action.",
        },
        {
          title: "Resume Choice",
          body: "Each row will show whether the MENA photo resume or NP resume is selected.",
        },
      ]}
    />
  );
}
