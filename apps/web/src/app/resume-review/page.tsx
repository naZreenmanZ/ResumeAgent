import { PlaceholderPage } from "@/components/PlaceholderPage";

export default function ResumeReviewPage() {
  return (
    <PlaceholderPage
      eyebrow="Resume Review"
      title="Inspect the tailored resume before upload."
      description="This workspace is prepared for side-by-side job requirements, final resume preview, change summary, and employer-facing QA checks."
      status="No tailored draft selected"
      primaryAction="Approve for upload"
      secondaryAction="Regenerate"
      emptyTitle="No tailored resume yet"
      emptyBody="Future issues will connect generated drafts and PDF previews. Issue 1 only establishes the review surface."
      panels={[
        {
          title: "Required Sections",
          body: "The review flow will verify the resume keeps its professional structure.",
          items: ["Professional Summary", "Professional Experience", "Technical Skills", "Education"],
        },
        {
          title: "Forbidden Labels",
          body: "Internal bot wording must never appear in the employer-facing resume.",
          items: ["No Targeted Summary", "No Base Resume Content", "No Job URL under name"],
        },
        {
          title: "Approval Gate",
          body: "Upload actions stay blocked until the reviewed PDF is approved.",
        },
      ]}
    />
  );
}
