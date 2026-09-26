export function getDashboardUrl() {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://orbitune-dashboard.vercel.app/dashboard";
  }
  return process.env.NEXT_PUBLIC_DASHBOARD_URL || "https://orbitune-dashboard.vercel.app/dashboard";
}
