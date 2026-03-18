import {
  getHeadcountAnalytics,
  getDiversityAnalytics,
  getCompensationAnalytics,
  getAttritionAnalytics,
  getHiringInsights,
  getWorkforceInsights,
  getGeographicInsights,
  getTerminationInsights,
  getCompensationInsights,
  getExecutiveSummary,
  getDeptGroupHierarchy,
  getClusterHierarchy,
  getRegionHierarchy,
  getDivisionHierarchy,
  getBranchManagerAnalytics,
} from "@/app/actions/analytics";
import { AnalyticsContent } from "@/components/analytics/analytics-content";

export const dynamic = "force-dynamic";

export default async function AnalyticsPage() {
  const [
    headcount,
    diversity,
    compensation,
    attrition,
    hiring,
    workforce,
    geographic,
    termination,
    compensationInsights,
    summary,
    deptGroupHierarchy,
    clusterHierarchy,
    regionHierarchy,
    divisionHierarchy,
    branchManagerAnalytics,
  ] = await Promise.all([
    getHeadcountAnalytics(),
    getDiversityAnalytics(),
    getCompensationAnalytics(),
    getAttritionAnalytics(),
    getHiringInsights(),
    getWorkforceInsights(),
    getGeographicInsights(),
    getTerminationInsights(),
    getCompensationInsights(),
    getExecutiveSummary(),
    getDeptGroupHierarchy(),
    getClusterHierarchy(),
    getRegionHierarchy(),
    getDivisionHierarchy(),
    getBranchManagerAnalytics(),
  ]);

  return (
    <AnalyticsContent
      headcount={headcount}
      diversity={diversity}
      compensation={compensation}
      attrition={attrition}
      hiring={hiring}
      workforce={workforce}
      geographic={geographic}
      termination={termination}
      compensationInsights={compensationInsights}
      summary={summary}
      deptGroupHierarchy={deptGroupHierarchy}
      clusterHierarchy={clusterHierarchy}
      regionHierarchy={regionHierarchy}
      divisionHierarchy={divisionHierarchy}
      branchManagerAnalytics={branchManagerAnalytics}
    />
  );
}
