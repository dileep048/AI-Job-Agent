const FAQS = [
  {
    q: "What does the AI Job Agent do?",
    a: "It is a workspace for your job search: profile, skills, experience, education, and resumes today. Matching, agent activity, and automated applications are being added next.",
  },
  {
    q: "How does the AI find jobs?",
    a: "Job discovery is not live yet. You can already capture preferences in your profile so matching can use them when it launches.",
  },
  {
    q: "Can I control which jobs the AI applies to?",
    a: "Yes. The product is designed so you stay in control of preferences and what gets submitted. Automatic apply will not send applications without a clear product flow for review.",
  },
  {
    q: "Can I review applications before they are submitted?",
    a: "That is the intended workflow. Application tracking in the dashboard will show what is ready, submitted, or waiting on you.",
  },
  {
    q: "Does the AI customize my resume?",
    a: "You can upload PDF or DOCX files and keep structured resume data as the source of truth. AI customization of that data is planned, not live in this version.",
  },
  {
    q: "Where can I track my applications?",
    a: "Use the Applications page in the dashboard. Tracking will expand as the agent starts submitting applications.",
  },
];

export function FAQ() {
  return (
    <section id="faq" className="scroll-mt-24 bg-background-soft">
      <div className="mx-auto max-w-3xl px-4 py-20 md:px-6">
        <h2 className="text-center text-3xl font-semibold tracking-tight md:text-4xl">FAQ</h2>
        <div className="mt-8 space-y-3">
          {FAQS.map((item) => (
            <details key={item.q} className="group rounded-card border border-line bg-white px-5 py-4">
              <summary className="cursor-pointer list-none font-medium text-ink">
                <span className="flex items-center justify-between gap-4">
                  {item.q}
                  <span className="text-muted group-open:hidden">+</span>
                  <span className="hidden text-muted group-open:inline">–</span>
                </span>
              </summary>
              <p className="mt-3 text-sm leading-relaxed text-muted">{item.a}</p>
            </details>
          ))}
        </div>
      </div>
    </section>
  );
}
