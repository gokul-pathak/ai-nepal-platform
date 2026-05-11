"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ReactNode } from "react";

import { useI18n } from "@/i18n/hooks/use-i18n";
import { LanguageSwitcher } from "@/components/language-switcher";

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { t } = useI18n();

  const links = [
    { href: "/", label: t("nav.home") },
    { href: "/tools", label: t("nav.tools") },
    { href: "/sponsors", label: t("nav.sponsors") },
    { href: "/admin", label: t("nav.admin") },
  ];

  return (
    <>
      <header className="sticky top-0 z-20 border-b border-border/70 bg-white/90 backdrop-blur">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-5 py-3 md:px-10">
          <Link href="/" className="text-sm font-semibold tracking-wide text-foreground">
            {t("brand.name")}
          </Link>
          <div className="flex flex-wrap items-center gap-3">
            <nav className="flex flex-wrap items-center gap-1" aria-label="Primary">
              {links.map((link) => {
                const active = pathname === link.href || (link.href !== "/" && pathname.startsWith(link.href));
                return (
                  <Link
                    key={link.href}
                    href={link.href}
                    className={`rounded-full px-3 py-1.5 text-sm transition ${
                      active ? "bg-[hsl(var(--muted))] text-foreground" : "text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    {link.label}
                  </Link>
                );
              })}
            </nav>
            <LanguageSwitcher />
          </div>
        </div>
      </header>
      {children}
    </>
  );
}
