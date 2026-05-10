"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { AdminMetricsResponse, getAdminMetrics } from "@/lib/api";

const ADMIN_KEY_STORAGE = "admin_api_key";

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

export default function AdminPage() {
  const [adminKey, setAdminKey] = useState("");
  const [metrics, setMetrics] = useState<AdminMetricsResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const saved = sessionStorage.getItem(ADMIN_KEY_STORAGE);
    if (saved) {
      setAdminKey(saved);
    }
  }, []);

  async function loadMetrics(key: string) {
    setLoading(true);
    setError("");
    try {
      const payload = await getAdminMetrics(key);
      setMetrics(payload);
    } catch (err) {
      setMetrics(null);
      setError(err instanceof Error ? err.message : "Failed to load metrics");
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!adminKey.trim()) {
      setError("Admin API key is required");
      return;
    }

    sessionStorage.setItem(ADMIN_KEY_STORAGE, adminKey.trim());
    await loadMetrics(adminKey.trim());
  }

  function handleLogout() {
    sessionStorage.removeItem(ADMIN_KEY_STORAGE);
    setAdminKey("");
    setMetrics(null);
    setError("");
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <section className="rounded-2xl border border-border/70 bg-white/85 p-6 shadow-sm md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Admin Metrics Access</p>
            <h1 className="mt-2 text-3xl font-semibold md:text-4xl">Admin Dashboard</h1>
            <p className="mt-3 text-sm text-muted-foreground">
              Enter admin API key to view internal metrics. The key is stored in session storage only.
            </p>
          </div>
          <Link
            href="/"
            className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
          >
            Back to home
          </Link>
        </div>

        <form className="mt-5 flex flex-wrap gap-3" onSubmit={handleSubmit}>
          <label htmlFor="admin-api-key" className="sr-only">
            Admin API key
          </label>
          <input
            id="admin-api-key"
            type="password"
            value={adminKey}
            onChange={(event) => setAdminKey(event.target.value)}
            placeholder="Enter admin API key"
            className="w-full max-w-md rounded-lg border border-border bg-white px-3 py-2 text-sm"
          />
          <button
            type="submit"
            disabled={loading}
            className="rounded-lg bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] disabled:opacity-60"
          >
            {loading ? "Loading..." : "Load metrics"}
          </button>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-lg border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground"
          >
            Clear key
          </button>
        </form>

        {error ? <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p> : null}
      </section>

      {metrics ? (
        <>
          <section className="mt-6 grid gap-4 sm:grid-cols-3">
            <article className="rounded-2xl border border-border/80 bg-white/85 p-5 shadow-sm">
              <p className="text-lg">📈</p>
              <h2 className="text-sm text-muted-foreground">Total requests</h2>
              <p className="mt-2 text-3xl font-semibold">{metrics.total_tool_usage_count.toLocaleString()}</p>
            </article>
            <article className="rounded-2xl border border-border/80 bg-white/85 p-5 shadow-sm">
              <p className="text-lg">👥</p>
              <h2 className="text-sm text-muted-foreground">Users helped</h2>
              <p className="mt-2 text-3xl font-semibold">{metrics.total_users_helped.toLocaleString()}</p>
            </article>
            <article className="rounded-2xl border border-border/80 bg-white/85 p-5 shadow-sm">
              <p className="text-lg">🤝</p>
              <h2 className="text-sm text-muted-foreground">Sponsor lead count</h2>
              <p className="mt-2 text-3xl font-semibold">{metrics.sponsor_lead_count.toLocaleString()}</p>
            </article>
          </section>

          <section className="mt-8 rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm">
            <h2 className="text-xl font-semibold">Most Used Tools</h2>
            <div className="mt-4 space-y-3">
              {metrics.usage_count_by_tool.map((item) => (
                <div key={item.tool_slug} className="flex items-center justify-between rounded-lg border border-border/70 px-4 py-3">
                  <span className="text-sm font-medium">{item.tool_slug}</span>
                  <span className="text-sm text-muted-foreground">{item.count.toLocaleString()} requests</span>
                </div>
              ))}
            </div>
          </section>

          <section className="mt-8 grid gap-6 lg:grid-cols-2">
            <article className="rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Latest Sponsor Leads</h2>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="text-muted-foreground">
                    <tr>
                      <th className="pb-2">Organization</th>
                      <th className="pb-2">Contact</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.latest_sponsor_leads.map((lead, idx) => (
                      <tr key={`${lead.organization_name}-${idx}`} className="border-t border-border/60">
                        <td className="py-2">{lead.organization_name}</td>
                        <td className="py-2">{lead.contact_name}</td>
                        <td className="py-2 capitalize">{lead.status}</td>
                        <td className="py-2 text-muted-foreground">{formatDate(lead.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>

            <article className="rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm">
              <h2 className="text-xl font-semibold">Latest Tool Usage</h2>
              <div className="mt-4 overflow-x-auto">
                <table className="min-w-full text-left text-sm">
                  <thead className="text-muted-foreground">
                    <tr>
                      <th className="pb-2">Tool</th>
                      <th className="pb-2">Language</th>
                      <th className="pb-2">Status</th>
                      <th className="pb-2">Created</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.latest_tool_usage_records.map((usage, idx) => (
                      <tr key={`${usage.tool_slug}-${idx}`} className="border-t border-border/60">
                        <td className="py-2">{usage.tool_slug}</td>
                        <td className="py-2 text-muted-foreground">{usage.language ?? "-"}</td>
                        <td className="py-2 capitalize">{usage.status}</td>
                        <td className="py-2 text-muted-foreground">{formatDate(usage.created_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </article>
          </section>
        </>
      ) : null}
    </main>
  );
}
