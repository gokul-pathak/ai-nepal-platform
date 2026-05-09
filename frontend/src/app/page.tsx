import Link from "next/link";

import { getPublicMetrics } from "@/lib/api";

const cards = [
  { href: "/tools", title: "Tools", body: "Explore upcoming AI utilities for Nepal." },
  { href: "/sponsors", title: "Sponsors", body: "See sponsorship model and partner direction." },
  { href: "/admin", title: "Admin", body: "Internal operations dashboard placeholder." },
];

export default async function HomePage() {
  let metrics: { total_requests: number; total_users_helped: number; total_sponsor_leads: number } | null = null;

  try {
    metrics = await getPublicMetrics();
  } catch {
    metrics = null;
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-12 md:px-10">
      <section className="relative overflow-hidden rounded-2xl border border-border/70 bg-white/75 p-8 shadow-sm backdrop-blur-sm md:p-12">
        <div className="pointer-events-none absolute -left-10 -top-8 h-36 w-36 rounded-full bg-rose-200/40 blur-2xl" />
        <div className="pointer-events-none absolute -right-12 bottom-0 h-40 w-40 rounded-full bg-orange-200/50 blur-2xl" />

        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">AI Nepal Platform</p>
        <h1 className="mt-3 max-w-4xl text-3xl font-semibold leading-tight md:text-5xl">
          Crafted for local rhythm, language, and everyday utility.
        </h1>
        <p className="mt-4 max-w-3xl text-base text-muted-foreground md:text-lg">
          Built with a grounded product foundation and a warm visual identity tuned for practical
          tools that feel close to home.
        </p>

        <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium">
          <span className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-rose-700">Namaste</span>
          <span className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-orange-700">Sajilo</span>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">Upayogi</span>
        </div>
      </section>

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="rounded-2xl border border-border/80 bg-white/80 p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <h2 className="text-xl font-semibold">{card.title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">{card.body}</p>
          </Link>
        ))}
      </section>

      <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm md:p-8">
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
          <p className="mt-4 rounded-lg bg-amber-50 px-4 py-3 text-sm text-amber-700">
            Metrics are temporarily unavailable. Please check backend connectivity.
          </p>
        )}
      </section>
    </main>
  );
}
