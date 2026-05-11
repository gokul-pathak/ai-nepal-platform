"use client";

import { useI18n } from "@/i18n/hooks/use-i18n";

export default function SponsorsLoading() {
  const { t } = useI18n();

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-10 md:px-10">
      <div className="flex flex-col items-center rounded-2xl border border-border/70 bg-white/85 px-8 py-10 text-center shadow-sm" role="status" aria-live="polite" aria-atomic="true">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-[hsl(var(--muted))] border-t-[hsl(var(--primary))]" aria-hidden="true" />
        <p className="mt-4 text-base font-medium">{t("common.pleaseWait")}</p>
        <p className="mt-1 text-sm text-muted-foreground">{t("loading.sponsors")}</p>
      </div>
    </main>
  );
}
