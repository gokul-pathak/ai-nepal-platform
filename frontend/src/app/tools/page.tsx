import Link from "next/link";

import { getTools } from "@/lib/api";

export default async function ToolsPage() {
  const tools = await getTools();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <header className="rounded-2xl border border-border/70 bg-white/70 p-6 shadow-sm backdrop-blur-sm md:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">AI Nepal Platform</p>
            <h1 className="mt-2 text-3xl font-semibold md:text-4xl">Tool Workspace</h1>
          </div>
          <Link
            href="/"
            className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
          >
            Home
          </Link>
        </div>
        <p className="mt-4 text-base text-muted-foreground">
          Pick any tool below. You can switch tools directly from each tool workspace without going back.
        </p>
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {tools.map((tool) => (
          <Link
            key={tool.id}
            href={`/tools/${tool.slug}`}
            className="group rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <h2 className="text-xl font-semibold group-hover:text-[hsl(var(--primary))]">{tool.name}</h2>
            <p className="mt-2 text-xs uppercase tracking-wide text-muted-foreground">{tool.slug}</p>
            <p className="mt-3 text-sm text-muted-foreground">
              {tool.description ?? "Run this tool to generate AI-assisted output."}
            </p>
            <p className="mt-5 text-sm font-medium text-[hsl(var(--primary))]">Open workspace</p>
          </Link>
        ))}
      </section>
    </main>
  );
}
