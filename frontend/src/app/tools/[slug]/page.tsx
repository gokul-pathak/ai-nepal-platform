"use client";

export const runtime = "edge";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import { runTool } from "@/lib/api";

const TOOL_NAMES: Record<string, string> = {
  translator: "Translator",
  "letter-writer": "Letter Writer",
  "form-helper": "Form Helper",
  "agriculture-helper": "Agriculture Helper",
  "legal-basic-helper": "Legal Basic Helper",
};

export default function ToolRunPage() {
  const params = useParams<{ slug: string }>();
  const slug = params.slug;
  const title = useMemo(() => TOOL_NAMES[slug] ?? slug, [slug]);

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
      setError("Input cannot be empty or just a single dot.");
      return;
    }

    setLoading(true);

    try {
      const response = await runTool(slug, { input, language });
      setResult(response.result);
      setRemaining(response.usage.remaining_daily_requests);
    } catch (err) {
      if (err instanceof TypeError) {
        setError("Backend is not reachable. Please ensure API server is running.");
      } else {
        const message = err instanceof Error ? err.message : "Something went wrong";
        if (message === "Daily free usage limit reached") {
          setError("You have reached your daily free limit (5 requests). Please try again tomorrow.");
        } else {
          setError(message);
        }
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <section className="rounded-2xl border border-border/70 bg-white/80 p-6 shadow-sm md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">AI Tool Workspace</p>
            <h1 className="mt-2 text-2xl font-semibold md:text-3xl">{title}</h1>
            <p className="mt-2 text-sm text-muted-foreground">Tool slug: {slug}</p>
          </div>
          <Link
            href="/"
            className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
          >
            Home
          </Link>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {Object.entries(TOOL_NAMES).map(([toolSlug, toolName]) => {
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
              Language
            </label>
            <select
              id="language"
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
            >
              <option value="en">English</option>
              <option value="ne">Nepali</option>
            </select>
          </div>

          <div>
            <label htmlFor="input" className="mb-2 block text-sm font-medium">
              Input
            </label>
            <textarea
              id="input"
              className="min-h-40 w-full rounded-lg border border-border bg-white px-3 py-2 text-sm"
              placeholder="Type your request here..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
              maxLength={4000}
            />
            <p className="mt-2 text-xs text-muted-foreground">Max 4000 characters.</p>
          </div>

          <button
            type="button"
            onClick={handleRun}
            disabled={loading || isInvalidInput}
            className="inline-flex items-center rounded-lg bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Running..." : "Run"}
          </button>
        </div>

        {error ? <p className="mt-4 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}

        {remaining !== null ? (
          <p className="mt-4 text-sm text-muted-foreground">Remaining daily requests: {remaining}</p>
        ) : null}

        {result ? (
          <div className="mt-4 rounded-lg border border-border bg-[hsl(var(--muted))] p-4">
            <h2 className="text-sm font-semibold">Result</h2>
            <p className="mt-2 whitespace-pre-wrap text-sm">{result}</p>
          </div>
        ) : null}
      </section>
    </main>
  );
}
