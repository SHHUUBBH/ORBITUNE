export function getDashboardUrl() {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_DASHBOARD_URL || "http://localhost:5173/dashboard";
  }
  return "http://localhost:5173/dashboard";
}
