export default function ToolsLoading() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10 md:px-10">
      <header className="rounded-2xl border border-border/70 bg-white/70 p-6 shadow-sm backdrop-blur-sm md:p-8">
        <div className="h-5 w-36 animate-pulse rounded bg-[hsl(var(--muted))]" />
        <div className="mt-3 h-10 w-60 animate-pulse rounded bg-[hsl(var(--muted))]" />
        <div className="mt-4 h-4 w-full max-w-xl animate-pulse rounded bg-[hsl(var(--muted))]" />
      </header>

      <section className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="rounded-2xl border border-border/80 bg-white/85 p-6 shadow-sm">
            <div className="h-6 w-2/3 animate-pulse rounded bg-[hsl(var(--muted))]" />
            <div className="mt-3 h-3 w-1/3 animate-pulse rounded bg-[hsl(var(--muted))]" />
            <div className="mt-4 h-4 w-full animate-pulse rounded bg-[hsl(var(--muted))]" />
            <div className="mt-2 h-4 w-5/6 animate-pulse rounded bg-[hsl(var(--muted))]" />
          </div>
        ))}
      </section>
    </main>
  );
}
