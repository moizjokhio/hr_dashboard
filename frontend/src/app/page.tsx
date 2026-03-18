import {
  getDashboardMetrics,
  getWorkflowWidgets,
  getOrgStructureMetrics,
  getCompensationMetrics,
} from "@/app/actions/dashboard";
import { DashboardContent } from "@/components/dashboard/dashboard-content";

export const dynamic = "force-dynamic"; // Ensure real-time data

export default async function HomePage() {
  // Fetch data in parallel
  const [metrics, workflow, orgStructure, compensation] = await Promise.all([
    getDashboardMetrics(),
    getWorkflowWidgets(),
    getOrgStructureMetrics(),
    getCompensationMetrics(),
  ]);

  return (
    <DashboardContent
      metrics={metrics}
      workflow={workflow}
      orgStructure={orgStructure}
      compensation={compensation}
    />
  );
}
