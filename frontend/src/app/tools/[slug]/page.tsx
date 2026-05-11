"use client";

export const runtime = "edge";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { runTool } from "@/lib/api";
import { useI18n } from "@/i18n/hooks/use-i18n";

function toFriendlyError(message: string, t: (key: string) => string): string {
  if (message === "Daily free usage limit reached") {
    return t("tools.errors.limit");
  }
  if (message.includes("X-Session-ID")) {
    return t("tools.errors.session");
  }
  if (message === "Input cannot be empty") {
    return t("tools.errors.invalidInput");
  }
  if (message === "Input contains disallowed instructions") {
    return t("tools.errors.blocked");
  }
  if (message === "AI provider request failed") {
    return t("tools.errors.provider");
  }
  return t("tools.errors.generic");
}

export default function ToolRunPage() {
  const { t } = useI18n();
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const toolNames = useMemo<Record<string, string>>(
    () => ({
      translator: t("toolNames.translator"),
      "letter-writer": t("toolNames.letterWriter"),
      "form-helper": t("toolNames.formHelper"),
      "agriculture-helper": t("toolNames.agricultureHelper"),
      "legal-basic-helper": t("toolNames.legalBasicHelper"),
    }),
    [t],
  );
  const title = useMemo(() => toolNames[slug] ?? slug, [slug, toolNames]);

  const [input, setInput] = useState("");
  const [language, setLanguage] = useState("en");
  const [result, setResult] = useState("");
  const [remaining, setRemaining] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const normalizedInput = input.trim();
  const isInvalidInput = normalizedInput.length === 0 || normalizedInput === ".";

  async function handleRun(): Promise<void> {
    setError("");
    setResult("");

    if (isInvalidInput) {
      setError(t("tools.errors.invalidInput"));
      return;
    }

    setLoading(true);

    try {
      const response = await runTool(slug, { input, language });
      setResult(response.result);
      setRemaining(response.usage.remaining_daily_requests);
    } catch (err) {
      if (err instanceof TypeError) {
        setError(t("tools.errors.backend"));
      } else {
        const message = err instanceof Error ? err.message : "Something went wrong";
        setError(toFriendlyError(message, t));
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-10">
      <section className="rounded-2xl border border-border/70 bg-white/80 p-6 shadow-sm md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("tools.workspaceLabel")}</p>
            <h1 className="mt-2 break-words text-2xl font-semibold md:text-3xl">{title}</h1>
            <p className="mt-2 break-all text-sm text-muted-foreground">{t("tools.slug")}: {slug}</p>
          </div>
          <Link
            href="/"
            className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
          >
            {t("nav.home")}
          </Link>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {Object.entries(toolNames).map(([toolSlug, toolName]) => {
            const isActive = toolSlug === slug;
            return (
              <Link
                key={toolSlug}
                href={`/tools/${toolSlug}`}
                className={`rounded-full border px-3 py-1.5 text-sm transition ${
                  isActive
                    ? "border-transparent bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]"
                    : "border-border bg-white text-muted-foreground hover:text-foreground"
                }`}
              >
                {toolName}
              </Link>
            );
          })}
        </div>

        <div className="mt-6 space-y-4">
          <div>
            <label htmlFor="language" className="mb-2 block text-sm font-medium">
              {t("tools.language")}
            </label>
            <select
              id="language"
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
            >
              <option value="en">{t("tools.english")}</option>
              <option value="ne">{t("tools.nepali")}</option>
            </select>
          </div>

          <div>
            <label htmlFor="input" className="mb-2 block text-sm font-medium">
              {t("tools.input")}
            </label>
            <textarea
              id="input"
              className="min-h-40 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
              placeholder={t("tools.inputPlaceholder")}
              value={input}
              onChange={(event) => setInput(event.target.value)}
              maxLength={4000}
            />
            <p className="mt-2 text-xs text-muted-foreground">{t("tools.maxChars")}</p>
          </div>

          <button
            type="button"
            onClick={handleRun}
            disabled={loading || isInvalidInput}
            className="inline-flex min-h-11 items-center rounded-lg bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] disabled:cursor-not-allowed disabled:opacity-60"
            aria-busy={loading}
          >
            {loading ? t("tools.running") : t("tools.run")}
          </button>
        </div>

        {error ? <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

        {remaining !== null ? (
          <p className="mt-4 text-sm text-muted-foreground">{t("tools.remaining")}: {remaining}</p>
        ) : null}

        {result ? (
          <div className="mt-4 rounded-lg border border-border bg-[hsl(var(--muted))] p-4">
            <h2 className="text-sm font-semibold">{t("tools.result")}</h2>
            <p className="mt-2 whitespace-pre-wrap text-sm">{result}</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
