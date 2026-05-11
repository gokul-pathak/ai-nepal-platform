import enCommon from "@/i18n/locales/en/common.json";
import neCommon from "@/i18n/locales/ne/common.json";

export const supportedLocales = ["en", "ne"] as const;

export type Locale = (typeof supportedLocales)[number];

export interface TranslationTree {
  [key: string]: string | TranslationTree;
}

const messageCatalog: Record<Locale, TranslationTree> = {
  en: enCommon as TranslationTree,
  ne: neCommon as TranslationTree,
};

export function getMessages(locale: Locale): TranslationTree {
  return messageCatalog[locale];
}
