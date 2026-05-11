"use client";

import { createContext, ReactNode, useEffect, useMemo, useState } from "react";

import { Locale, supportedLocales } from "@/i18n/utils/messages";
import { translate } from "@/i18n/utils/translate";

const STORAGE_KEY = "ai_nepal_locale";

type I18nContextValue = {
  locale: Locale;
  setLocale: (locale: Locale) => void;
  t: (key: string, params?: Record<string, string | number>) => string;
};

export const I18nContext = createContext<I18nContextValue | null>(null);

function isSupportedLocale(value: string): value is Locale {
  return supportedLocales.includes(value as Locale);
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("en");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored && isSupportedLocale(stored)) {
      setLocaleState(stored);
      return;
    }

    const browserLocale = window.navigator.language.toLowerCase().startsWith("ne") ? "ne" : "en";
    setLocaleState(browserLocale);
  }, []);

  useEffect(() => {
    document.documentElement.lang = locale;
    window.localStorage.setItem(STORAGE_KEY, locale);
  }, [locale]);

  const value = useMemo<I18nContextValue>(
    () => ({
      locale,
      setLocale: setLocaleState,
      t: (key, params) => translate(locale, key, params),
    }),
    [locale],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
