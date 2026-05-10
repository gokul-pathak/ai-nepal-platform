import Link from "next/link";

type ToolCardProps = {
  href: string;
  title: string;
  slug?: string;
  description: string;
  ctaLabel?: string;
};

export function ToolCard({ href, title, slug, description, ctaLabel = "Open tool" }: ToolCardProps) {
  return (
    <Link
      href={href}
      className="group flex h-full flex-col rounded-2xl border border-border/80 bg-white/90 p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
      aria-label={`${title} tool`}
    >
      <div className="flex items-start justify-between gap-3">
        <h3 className="text-lg font-semibold leading-snug group-hover:text-[hsl(var(--primary))]">{title}</h3>
        {slug ? (
          <span className="rounded-full border border-border bg-[hsl(var(--muted))] px-2.5 py-1 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
            {slug}
          </span>
        ) : null}
      </div>
      <p className="mt-3 text-sm leading-6 text-muted-foreground">{description}</p>
      <span className="mt-5 inline-flex items-center text-sm font-medium text-[hsl(var(--primary))]">{ctaLabel}</span>
    </Link>
  );
}
