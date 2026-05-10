import Link from "next/link";

import { getTools } from "@/lib/api";
import { StateMessage } from "@/components/state-message";
import { ToolCard } from "@/components/tool-card";

export const runtime = "edge";

export default async function ToolsPage() {
  let tools: Awaited<ReturnType<typeof getTools>> = [];
  let loadFailed = false;

  try {
    tools = await getTools();
  } catch {
    loadFailed = true;
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-10">
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

      <section className="mt-8" aria-live="polite">
        {loadFailed ? (
          <StateMessage tone="warning" message="Tools are temporarily unavailable. Please refresh in a moment." />
        ) : null}

        {!loadFailed && tools.length === 0 ? (
          <StateMessage tone="info" message="No tools are available right now. Please check again soon." />
        ) : null}

        {tools.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tools.map((tool) => (
              <ToolCard
                key={tool.id}
                href={`/tools/${tool.slug}`}
                title={tool.name}
                slug={tool.slug}
                description={tool.description ?? "Run this tool to generate AI-assisted output."}
                ctaLabel="Open workspace"
              />
            ))}
          </div>
        ) : null}
      </section>
    </main>
  );
}
