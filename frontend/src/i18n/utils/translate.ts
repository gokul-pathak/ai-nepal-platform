import { getMessages, Locale, TranslationTree } from "@/i18n/utils/messages";

type TranslateParams = Record<string, string | number>;

function getNestedValue(messages: TranslationTree, key: string): string | undefined {
  const parts = key.split(".");
  let current: string | TranslationTree | undefined = messages;

  for (const part of parts) {
    if (!current || typeof current === "string") {
      return undefined;
    }
    current = current[part];
  }

  return typeof current === "string" ? current : undefined;
}

function interpolate(template: string, params?: TranslateParams): string {
  if (!params) {
    return template;
  }

  return template.replace(/\{\{\s*(\w+)\s*\}\}/g, (_, token: string) => {
    const value = params[token];
    return value === undefined ? "" : String(value);
  });
}

export function translate(locale: Locale, key: string, params?: TranslateParams): string {
  const localeMessages = getMessages(locale);
  const fallbackMessages = getMessages("en");

  const localized = getNestedValue(localeMessages, key);
  if (localized !== undefined) {
    return interpolate(localized, params);
  }

  const fallback = getNestedValue(fallbackMessages, key);
  if (fallback !== undefined) {
    return interpolate(fallback, params);
  }

  return key;
}
