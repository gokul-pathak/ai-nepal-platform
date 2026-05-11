"use client";

import { FormEvent, useEffect, useState } from "react";
import Link from "next/link";

import { createSponsorLead, getSponsorPackages, SponsorPackage } from "@/lib/api";
import { StateMessage } from "@/components/state-message";
import { useI18n } from "@/i18n/hooks/use-i18n";

type FormState = {
  organization_name: string;
  contact_name: string;
  email: string;
  phone: string;
  sponsor_type: string;
  budget_range: string;
  target_group: string;
  message: string;
};

const INITIAL_FORM: FormState = {
  organization_name: "",
  contact_name: "",
  email: "",
  phone: "",
  sponsor_type: "",
  budget_range: "",
  target_group: "",
  message: "",
};

function toFriendlyFormError(err: unknown, t: (key: string) => string): string {
  if (err instanceof TypeError) {
    return t("sponsors.errors.service");
  }
  if (err instanceof Error) {
    if (err.message.toLowerCase().includes("email")) {
      return t("sponsors.errors.emailCheck");
    }
    return t("sponsors.errors.generic");
  }
  return t("sponsors.errors.generic");
}

export default function SponsorsPage() {
  const { t } = useI18n();
  const [packages, setPackages] = useState<SponsorPackage[]>([]);
  const [loadingPackages, setLoadingPackages] = useState(true);
  const [packageError, setPackageError] = useState("");

  const [form, setForm] = useState<FormState>(INITIAL_FORM);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    let active = true;
    async function loadPackages() {
      setLoadingPackages(true);
      setPackageError("");
      try {
        const data = await getSponsorPackages();
        if (active) {
          setPackages(data);
        }
      } catch {
        if (active) {
          setPackageError(t("sponsors.packagesUnavailable"));
        }
      } finally {
        if (active) {
          setLoadingPackages(false);
        }
      }
    }

    void loadPackages();
    return () => {
      active = false;
    };
  }, [t]);

  function setField<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function validateForm(): string | null {
    if (form.organization_name.trim().length < 2) {
      return t("sponsors.errors.organization");
    }
    if (form.contact_name.trim().length < 2) {
      return t("sponsors.errors.contact");
    }
    if (!form.email.includes("@")) {
      return t("sponsors.errors.email");
    }
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError("");
    setSuccessMessage("");

    const validationError = validateForm();
    if (validationError) {
      setFormError(validationError);
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        organization_name: form.organization_name.trim(),
        contact_name: form.contact_name.trim(),
        email: form.email.trim(),
        phone: form.phone.trim() || undefined,
        sponsor_type: form.sponsor_type.trim() || undefined,
        budget_range: form.budget_range.trim() || undefined,
        target_group: form.target_group.trim() || undefined,
        message: form.message.trim() || undefined,
      };

      const response = await createSponsorLead(payload);
      setSuccessMessage(response.message);
      setForm(INITIAL_FORM);
    } catch (err) {
      setFormError(toFriendlyFormError(err, t));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-5 py-8 md:px-10 md:py-10">
      <section className="rounded-2xl border border-border/70 bg-white/80 p-6 shadow-sm md:p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{t("brand.name")}</p>
            <h1 className="mt-2 text-3xl font-semibold md:text-4xl">{t("sponsors.title")}</h1>
            <p className="mt-4 max-w-3xl text-base text-muted-foreground">{t("sponsors.body")}</p>
          </div>

          <div className="flex gap-2">
            <Link
              href="/"
              className="rounded-full border border-border bg-white px-4 py-2 text-sm font-medium text-muted-foreground transition hover:text-foreground"
            >
              {t("nav.home")}
            </Link>
          </div>
        </div>
      </section>

      <section className="mt-8">
        <h2 className="text-2xl font-semibold">{t("sponsors.packagesTitle")}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{t("sponsors.packagesBody")}</p>

        {packageError ? <div className="mt-4"><StateMessage tone="warning" message={packageError} /></div> : null}

        <div className="mt-5 grid gap-4 md:grid-cols-3">
          {loadingPackages
            ? Array.from({ length: 3 }).map((_, idx) => (
                <div key={idx} className="rounded-2xl border border-border/80 bg-white/85 p-5 shadow-sm">
                  <div className="h-6 w-2/3 animate-pulse rounded bg-[hsl(var(--muted))]" />
                  <div className="mt-3 space-y-2">
                    <div className="h-3 w-full animate-pulse rounded bg-[hsl(var(--muted))]" />
                    <div className="h-3 w-full animate-pulse rounded bg-[hsl(var(--muted))]" />
                    <div className="h-3 w-5/6 animate-pulse rounded bg-[hsl(var(--muted))]" />
                  </div>
                  <div className="mt-4 h-4 w-3/4 animate-pulse rounded bg-[hsl(var(--muted))]" />
                </div>
              ))
            : packages.map((item) => (
                <article key={item.id} className="rounded-2xl border border-border/80 bg-white/85 p-5 shadow-sm">
                  <h3 className="text-xl font-semibold">{item.name}</h3>
                  <p className="mt-2 text-sm text-muted-foreground">{item.price_label ?? t("sponsors.customPartnership")}</p>
                  <p className="mt-3 text-sm text-muted-foreground">{item.description}</p>
                  <p className="mt-4 text-sm font-medium text-[hsl(var(--primary))]">
                    {t("sponsors.monthlySupport")}: {item.monthly_request_limit.toLocaleString()}
                  </p>
                </article>
              ))}
        </div>

        {!loadingPackages && !packageError && packages.length === 0 ? (
          <div className="mt-4">
            <StateMessage tone="info" message={t("sponsors.packagesEmpty")} />
          </div>
        ) : null}
      </section>

      <section className="mt-8 rounded-2xl border border-border/70 bg-white/85 p-6 shadow-sm md:p-8">
        <h2 className="text-2xl font-semibold">{t("sponsors.formTitle")}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{t("sponsors.formBody")}</p>

        <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.organization")} *</span>
            <input
              value={form.organization_name}
              onChange={(event) => setField("organization_name", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
              required
            />
          </label>

          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.contact")} *</span>
            <input
              value={form.contact_name}
              onChange={(event) => setField("contact_name", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
              required
            />
          </label>

          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.email")} *</span>
            <input
              type="email"
              value={form.email}
              onChange={(event) => setField("email", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
              required
            />
          </label>

          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.phone")}</span>
            <input
              value={form.phone}
              onChange={(event) => setField("phone", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
            />
          </label>

          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.type")}</span>
            <input
              value={form.sponsor_type}
              onChange={(event) => setField("sponsor_type", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
            />
          </label>

          <label className="text-sm">
            <span className="mb-1 block font-medium">{t("sponsors.fields.budget")}</span>
            <input
              value={form.budget_range}
              onChange={(event) => setField("budget_range", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
            />
          </label>

          <label className="text-sm md:col-span-2">
            <span className="mb-1 block font-medium">{t("sponsors.fields.target")}</span>
            <input
              value={form.target_group}
              onChange={(event) => setField("target_group", event.target.value)}
              className="w-full rounded-lg border border-border bg-white px-3 py-2"
            />
          </label>

          <label className="text-sm md:col-span-2">
            <span className="mb-1 block font-medium">{t("sponsors.fields.message")}</span>
            <textarea
              value={form.message}
              onChange={(event) => setField("message", event.target.value)}
              className="min-h-28 w-full rounded-lg border border-border bg-white px-3 py-2"
              placeholder={t("sponsors.fields.messagePlaceholder")}
            />
          </label>

          <div className="md:col-span-2">
            <button
              type="submit"
              disabled={submitting}
              className="min-h-11 rounded-lg bg-[hsl(var(--primary))] px-4 py-2 text-sm font-medium text-[hsl(var(--primary-foreground))] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))] disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? t("sponsors.submitting") : t("sponsors.submit")}
            </button>

            {formError ? <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-700">{formError}</p> : null}
            {successMessage ? <p className="mt-3 rounded-lg bg-green-50 px-3 py-2 text-sm text-green-700">{successMessage}</p> : null}
          </div>
        </form>
      </section>
    </main>
  );
}
