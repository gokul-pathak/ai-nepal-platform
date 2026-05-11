"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { getTools, Tool } from "@/lib/api";
import { StateMessage } from "@/components/state-message";
import { ToolCard } from "@/components/tool-card";
import { useI18n } from "@/i18n/hooks/use-i18n";

export default function ToolsClient() {
  const { t } = useI18n();
  const [tools, setTools] = useState<Tool[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadFailed, setLoadFailed] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadTools() {
      setLoading(true);
      setLoadFailed(false);
      try {
        const data = await getTools();
        if (active) {
          setTools(data);
        }
      } catch {
        if (active) {
          setLoadFailed(true);
          setTools([]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    void loadTools();
    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-10">
      <header className="rounded-2xl border border-border/70 bg-white/70 p-6 shadow-sm backdrop-blur-sm md:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("tools.headerLabel")}</p>
            <h1 className="mt-2 text-3xl font-semibold md:text-4xl">{t("tools.headerTitle")}</h1>
          </div>
          <Link
            href="/"
            className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
          >
            {t("nav.home")}
          </Link>
        </div>
        <p className="mt-4 text-base text-muted-foreground">{t("tools.headerBody")}</p>
      </header>

      <section className="mt-8" aria-live="polite">
        {loading ? <StateMessage tone="info" message={t("common.loading")} /> : null}
        {loadFailed ? <StateMessage tone="warning" message={t("tools.unavailable")} /> : null}
        {!loading && !loadFailed && tools.length === 0 ? <StateMessage tone="info" message={t("tools.empty")} /> : null}

        {tools.length > 0 ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {tools.map((tool) => (
              <ToolCard
                key={tool.id}
                href={`/tools/${tool.slug}`}
                title={tool.name}
                slug={tool.slug}
                description={tool.description ?? t("tools.defaultDescription")}
                ctaLabel={t("common.openWorkspace")}
                ariaLabel={`${tool.name} ${t("common.openWorkspace")}`}
              />
            ))}
          </div>
        ) : null}
      </section>
    </main>
  );
}
