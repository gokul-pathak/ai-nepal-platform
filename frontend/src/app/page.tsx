import Link from "next/link";

import { getPublicMetrics } from "@/lib/api";
import { ToolCard } from "@/components/tool-card";
import { StateMessage } from "@/components/state-message";

const toolHighlights = [
  {
    href: "/tools/translator",
    title: "Translator",
    slug: "translator",
    body: "Translate local communication quickly between Nepali and English.",
  },
  {
    href: "/tools/letter-writer",
    title: "Letter Writer",
    slug: "letter-writer",
    body: "Draft polite letters for schools, offices, banks, and services.",
  },
  {
    href: "/tools/form-helper",
    title: "Form Helper",
    slug: "form-helper",
    body: "Get guided text for common form fields with clear language.",
  },
];

export default async function HomePage() {
  let metrics: { total_requests: number; total_users_helped: number; total_sponsor_leads: number } | null = null;

  try {
    metrics = await getPublicMetrics();
  } catch {
    metrics = null;
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-12">
      <section className="relative overflow-hidden rounded-3xl border border-border/70 bg-white/80 p-7 shadow-sm backdrop-blur-sm md:p-12">
        <div className="pointer-events-none absolute -left-10 -top-8 h-36 w-36 rounded-full bg-rose-200/40 blur-2xl" />
        <div className="pointer-events-none absolute -right-12 bottom-0 h-40 w-40 rounded-full bg-orange-200/50 blur-2xl" />

        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">AI Nepal Platform</p>
        <h1 className="mt-3 max-w-4xl text-3xl font-semibold leading-tight md:text-5xl">
          Practical AI support for students, SMEs, and communities across Nepal.
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-muted-foreground md:text-lg">
          We build simple, trustworthy tools for everyday tasks: writing, translating, and understanding forms with
          language that feels local and clear.
        </p>

        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href="/tools"
            className="rounded-lg bg-[hsl(var(--primary))] px-5 py-2.5 text-sm font-medium text-[hsl(var(--primary-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
          >
            Explore tools
          </Link>
          <Link
            href="/sponsors"
            className="rounded-lg border border-border bg-white px-5 py-2.5 text-sm font-medium text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
          >
            Sponsor the mission
          </Link>
        </div>

        <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium">
          <span className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-rose-700">Namaste</span>
          <span className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-orange-700">Sajilo</span>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">Upayogi</span>
        </div>
      </section>

      <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm md:p-8">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Mission</p>
        <h2 className="mt-2 text-2xl font-semibold md:text-3xl">Digital help that is useful, affordable, and inclusive</h2>
        <p className="mt-3 max-w-4xl text-sm leading-7 text-muted-foreground md:text-base">
          The platform focuses on practical outcomes: saving time for small businesses, helping students draft better
          writing, and supporting first-time digital users with guided AI tools.
        </p>
      </section>

      <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm md:p-8" aria-live="polite">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Public Impact</p>
        <h2 className="mt-2 text-2xl font-semibold md:text-3xl">Platform Snapshot</h2>

        {metrics ? (
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">Total requests</p>
              <p className="mt-2 text-2xl font-semibold">{metrics.total_requests.toLocaleString()}</p>
            </article>
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">Users helped</p>
              <p className="mt-2 text-2xl font-semibold">{metrics.total_users_helped.toLocaleString()}</p>
            </article>
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">Sponsor interests</p>
              <p className="mt-2 text-2xl font-semibold">{metrics.total_sponsor_leads.toLocaleString()}</p>
            </article>
          </div>
        ) : (
          <div className="mt-4">
            <StateMessage tone="warning" message="Live impact metrics are temporarily unavailable. Please check back soon." />
          </div>
        )}
      </section>

      <section className="mt-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">AI Tools</p>
            <h2 className="mt-2 text-2xl font-semibold md:text-3xl">Built for everyday tasks</h2>
          </div>
          <Link href="/tools" className="text-sm font-medium text-[hsl(var(--primary))]">
            View all tools
          </Link>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {toolHighlights.map((tool) => (
            <ToolCard key={tool.slug} href={tool.href} title={tool.title} slug={tool.slug} description={tool.body} />
          ))}
        </div>
      </section>

      <section className="mt-8 rounded-2xl border border-border/70 bg-[hsl(var(--muted))] p-6 md:p-8">
        <h2 className="text-2xl font-semibold md:text-3xl">Support AI access for underserved communities</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground md:text-base">
          Sponsor packages help keep AI assistance available for students, rural entrepreneurs, and grassroots programs.
        </p>
        <div className="mt-5">
          <Link
            href="/sponsors"
            className="inline-flex rounded-lg bg-[hsl(var(--primary))] px-5 py-2.5 text-sm font-medium text-[hsl(var(--primary-foreground))]"
          >
            Become a sponsor
          </Link>
        </div>
      </section>

      <footer className="mt-10 border-t border-border/80 py-6 text-sm text-muted-foreground">
        <p>AI Nepal Platform - public-good AI utilities for Nepal.</p>
      </footer>
    </main>
  );
}
