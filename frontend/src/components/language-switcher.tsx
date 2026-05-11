"use client";

import { useI18n } from "@/i18n/hooks/use-i18n";

export function LanguageSwitcher() {
  const { locale, setLocale, t } = useI18n();

  return (
    <div className="inline-flex items-center gap-1 rounded-full border border-border bg-white p-1" role="group" aria-label={t("lang.label")}>
      <button
        type="button"
        onClick={() => setLocale("en")}
        aria-pressed={locale === "en"}
        className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
          locale === "en" ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]" : "text-muted-foreground"
        }`}
      >
        {t("lang.en")}
      </button>
      <button
        type="button"
        onClick={() => setLocale("ne")}
        aria-pressed={locale === "ne"}
        className={`rounded-full px-3 py-1.5 text-xs font-semibold transition ${
          locale === "ne" ? "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]" : "text-muted-foreground"
        }`}
      >
        {t("lang.ne")}
      </button>
    </div>
  );
}
