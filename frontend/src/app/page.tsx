import Link from "next/link";

const cards = [
  { href: "/tools", title: "Tools", body: "Explore upcoming AI utilities for Nepal." },
  { href: "/sponsors", title: "Sponsors", body: "See sponsorship model and partner direction." },
  { href: "/admin", title: "Admin", body: "Internal operations dashboard placeholder." },
];

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-12 md:px-10">
      <section className="rounded-2xl border border-border/70 bg-white/70 p-8 shadow-sm backdrop-blur-sm md:p-12">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-muted-foreground">
          AI Nepal Platform
        </p>
        <h1 className="mt-3 text-3xl font-semibold leading-tight md:text-5xl">
          Clean monorepo foundation ready for production-grade iterations.
        </h1>
        <p className="mt-4 max-w-3xl text-base text-muted-foreground md:text-lg">
          This initial release focuses on architecture, security, CI, and developer workflow.
          Business features are intentionally deferred to future pull requests.
        </p>
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
    </main>
  );
}
