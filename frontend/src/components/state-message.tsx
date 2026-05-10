type StateMessageProps = {
  tone?: "error" | "warning" | "info";
  message: string;
};

const toneClass: Record<NonNullable<StateMessageProps["tone"]>, string> = {
  error: "bg-red-50 text-red-800 border-red-200",
  warning: "bg-amber-50 text-amber-800 border-amber-200",
  info: "bg-blue-50 text-blue-800 border-blue-200",
};

export function StateMessage({ tone = "info", message }: StateMessageProps) {
  return <p className={`rounded-lg border px-3 py-2 text-sm ${toneClass[tone]}`}>{message}</p>;
}
