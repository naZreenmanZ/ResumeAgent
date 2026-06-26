import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function SettingsPage() {
  return (
    <PlaceholderPage
      eyebrow="Settings"
      title="Control local paths, schedule, and approval mode."
      description="Settings will eventually manage base resume paths, runtime folders, target roles, target skills, blocked keywords, scan interval, and approval mode."
      status="Local config not connected"
      primaryAction="Save settings"
      secondaryAction="Check folders"
      emptyTitle="Settings are not editable yet"
      emptyBody="Issue 1 keeps settings as a placeholder. Config editing belongs with backend integration and safety checks."
      panels={[
        {
          title: "Runtime Folders",
          body: "The UI will show whether resumes, tailored resumes, tracking, and imports folders exist.",
        },
        {
          title: "Approval Mode",
          body: "Full-auto mode must be intentional and clearly warned before enabling.",
        },
        {
          title: "Git Safety",
          body: "Private config, resumes, trackers, and imports remain ignored.",
        },
      ]}
    />
  );
}
