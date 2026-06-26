import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function ApplicationFlowPage() {
  return (
    <PlaceholderPage
      eyebrow="Application Flow"
      title="Make every portal step visible before submit."
      description="This view reserves space for login state, CV upload state, modal detection, duplicate detection, manual action, and final approval."
      status="No active application"
      primaryAction="Open portal"
      secondaryAction="Mark already applied"
      emptyTitle="No application in progress"
      emptyBody="The shell models the future guided workflow without automating any portal action in Issue 1."
      panels={[
        {
          title: "State Clarity",
          body: "Portal steps should be specific and recoverable.",
          items: ["Login required", "Upload success", "Ready for submit"],
        },
        {
          title: "Manual Safe Points",
          body: "If file upload needs help, the UI will show the exact PDF path and confirmation step.",
        },
        {
          title: "Submit Control",
          body: "Final submit remains explicit and separate from navigation.",
        },
      ]}
    />
  );
}
