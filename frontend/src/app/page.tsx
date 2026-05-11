"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { getPublicMetrics } from "@/lib/api";
import { ToolCard } from "@/components/tool-card";
import { StateMessage } from "@/components/state-message";
import { useI18n } from "@/i18n/hooks/use-i18n";

type PublicMetrics = { total_requests: number; total_users_helped: number; total_sponsor_leads: number };

export default function HomePage() {
  const { t, locale } = useI18n();
  const [metrics, setMetrics] = useState<PublicMetrics | null>(null);
  const [isMetricsLoading, setIsMetricsLoading] = useState<boolean>(true);
  const [metricsError, setMetricsError] = useState<boolean>(false);

  const toolHighlights = useMemo(
    () => [
      {
        href: "/tools/translator",
        title: t("toolNames.translator"),
        slug: "translator",
        body: t("landing.toolTranslator"),
      },
      {
        href: "/tools/letter-writer",
        title: t("toolNames.letterWriter"),
        slug: "letter-writer",
        body: t("landing.toolLetterWriter"),
      },
      {
        href: "/tools/form-helper",
        title: t("toolNames.formHelper"),
        slug: "form-helper",
        body: t("landing.toolFormHelper"),
      },
    ],
    [t],
  );

  useEffect(() => {
    let active = true;
    async function loadMetrics() {
      try {
        const data = await getPublicMetrics();
        if (active) {
          setMetrics(data);
          setIsMetricsLoading(false);
        }
      } catch {
        if (active) {
          setMetricsError(true);
          setIsMetricsLoading(false);
        }
      }
    }
    void loadMetrics();
    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-12">
      <section className="relative overflow-hidden rounded-3xl border border-border/70 bg-white/80 p-7 shadow-sm backdrop-blur-sm md:p-12">
        <div className="pointer-events-none absolute -left-10 -top-8 h-36 w-36 rounded-full bg-rose-200/40 blur-2xl" />
        <div className="pointer-events-none absolute -right-12 bottom-0 h-40 w-40 rounded-full bg-orange-200/50 blur-2xl" />

        <p className="text-sm font-medium uppercase tracking-[0.24em] text-muted-foreground">{t("brand.name")}</p>
        <h1 className="mt-3 max-w-4xl text-3xl font-semibold leading-tight md:text-5xl">
          {t("landing.heroTitle")}
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-muted-foreground md:text-lg">
          {t("landing.heroBody")}
        </p>

        <div className="mt-7 flex flex-wrap gap-3">
          <Link
            href="/tools"
            className="rounded-lg bg-[hsl(var(--primary))] px-5 py-2.5 text-sm font-medium text-[hsl(var(--primary-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
          >
            {t("landing.ctaTools")}
          </Link>
          <Link
            href="/sponsors"
            className="rounded-lg border border-border bg-white px-5 py-2.5 text-sm font-medium text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
          >
            {t("landing.ctaSponsors")}
          </Link>
        </div>

        <div className="mt-6 flex flex-wrap gap-2 text-xs font-medium">
          <span className="rounded-full border border-rose-200 bg-rose-50 px-3 py-1 text-rose-700">Namaste</span>
          <span className="rounded-full border border-orange-200 bg-orange-50 px-3 py-1 text-orange-700">Sajilo</span>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">Upayogi</span>
        </div>
      </section>

      <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm md:p-8">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("landing.missionLabel")}</p>
        <h2 className="mt-2 text-2xl font-semibold md:text-3xl">{t("landing.missionTitle")}</h2>
        <p className="mt-3 max-w-4xl text-sm leading-7 text-muted-foreground md:text-base">
          {t("landing.missionBody")}
        </p>
      </section>

      <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm md:p-8" aria-live="polite">
        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("landing.impactLabel")}</p>
        <h2 className="mt-2 text-2xl font-semibold md:text-3xl">{t("landing.impactTitle")}</h2>

        {isMetricsLoading ? (
          <div className="mt-6 flex items-center justify-center py-8" role="status" aria-live="polite">
            <div className="text-sm text-muted-foreground">{t("common.loading")}</div>
          </div>
        ) : metrics ? (
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">{t("landing.totalRequests")}</p>
              <p className="mt-2 text-2xl font-semibold">{new Intl.NumberFormat(locale).format(metrics.total_requests)}</p>
            </article>
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">{t("landing.usersHelped")}</p>
              <p className="mt-2 text-2xl font-semibold">{new Intl.NumberFormat(locale).format(metrics.total_users_helped)}</p>
            </article>
            <article className="rounded-xl border border-border/70 bg-white px-4 py-4">
              <p className="text-sm text-muted-foreground">{t("landing.sponsorInterests")}</p>
              <p className="mt-2 text-2xl font-semibold">{new Intl.NumberFormat(locale).format(metrics.total_sponsor_leads)}</p>
            </article>
          </div>
        ) : metricsError ? (
          <div className="mt-4" role="alert" aria-live="assertive">
            <StateMessage tone="warning" message={t("landing.impactUnavailable")} />
          </div>
        ) : null}
      </section>

      <section className="mt-8">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("landing.toolsLabel")}</p>
            <h2 className="mt-2 text-2xl font-semibold md:text-3xl">{t("landing.toolsTitle")}</h2>
          </div>
          <Link href="/tools" className="text-sm font-medium text-[hsl(var(--primary))]">
            {t("common.viewAllTools")}
          </Link>
        </div>
        <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {toolHighlights.map((tool) => (
            <ToolCard
              key={tool.slug}
              href={tool.href}
              title={tool.title}
              slug={tool.slug}
              description={tool.body}
              ctaLabel={t("common.openTool")}
              ariaLabel={t("common.openToolAria", { toolName: tool.title })}
            />
          ))}
        </div>
      </section>

      <section className="mt-8 rounded-2xl border border-border/70 bg-[hsl(var(--muted))] p-6 md:p-8">
        <h2 className="text-2xl font-semibold md:text-3xl">{t("landing.sponsorTitle")}</h2>
        <p className="mt-3 max-w-3xl text-sm leading-7 text-muted-foreground md:text-base">
          {t("landing.sponsorBody")}
        </p>
        <div className="mt-5">
          <Link
            href="/sponsors"
            className="inline-flex rounded-lg bg-[hsl(var(--primary))] px-5 py-2.5 text-sm font-medium text-[hsl(var(--primary-foreground))]"
          >
            {t("landing.sponsorCta")}
          </Link>
        </div>
      </section>

      <footer className="mt-10 border-t border-border/80 py-6 text-sm text-muted-foreground">
        <p>{t("brand.tagline")}</p>
      </footer>
    </main>
  );
}
