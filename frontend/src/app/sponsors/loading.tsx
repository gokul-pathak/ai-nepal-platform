export default function SponsorsLoading() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl items-center justify-center px-6 py-10 md:px-10">
      <div className="flex flex-col items-center rounded-2xl border border-border/70 bg-white/85 px-8 py-10 text-center shadow-sm">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-[hsl(var(--muted))] border-t-[hsl(var(--primary))]" />
        <p className="mt-4 text-base font-medium">Please wait...</p>
        <p className="mt-1 text-sm text-muted-foreground">Loading sponsor workspace</p>
      </div>
    </main>
  );
}
