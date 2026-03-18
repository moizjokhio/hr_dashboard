"use client";

import { AlertTriangle, Clock, ShieldAlert } from "lucide-react";
import Link from "next/link";

interface WorkflowItem {
  EMPLOYEE_NUMBER: string;
  EMPLOYEE_FULL_NAME: string;
  DEPARTMENT_NAME?: string;
  DATE_PROBATION_END?: string;
  DATE_OF_BIRTH?: string;
  ACTION_REASON?: string;
  CONFIRMED_DATE?: string;
}

interface HRWorkflowProps {
  probationCliff: WorkflowItem[];
  retirementRadar: WorkflowItem[];
  disciplinaryWatch: WorkflowItem[];
}

export function HRWorkflow({
  probationCliff,
  retirementRadar,
  disciplinaryWatch,
}: HRWorkflowProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
      {/* Probation Cliff */}
      <WorkflowCard
        title="Probation Cliff"
        icon={<Clock className="w-5 h-5 text-amber-600" />}
        description="Probation ending < 30 days"
        items={probationCliff}
        type="probation"
      />

      {/* Retirement Radar */}
      <WorkflowCard
        title="Retirement Radar"
        icon={<UsersIcon className="w-5 h-5 text-blue-600" />}
        description="Retiring within 60 days"
        items={retirementRadar}
        type="retirement"
      />

      {/* Disciplinary Watch */}
      <WorkflowCard
        title="Disciplinary Watch"
        icon={<ShieldAlert className="w-5 h-5 text-red-600" />}
        description="Recent disciplinary actions"
        items={disciplinaryWatch}
        type="disciplinary"
      />
    </div>
  );
}

function UsersIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function WorkflowCard({
  title,
  icon,
  description,
  items,
  type,
}: {
  title: string;
  icon: React.ReactNode;
  description: string;
  items: WorkflowItem[];
  type: "probation" | "retirement" | "disciplinary";
}) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col h-full">
      <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gray-50/50 rounded-t-xl">
        <div>
          <h3 className="font-semibold text-gray-900 flex items-center gap-2">
            {icon}
            {title}
          </h3>
          <p className="text-xs text-gray-500 mt-1">{description}</p>
        </div>
        <span className="bg-white px-2 py-1 rounded-md text-xs font-medium border border-gray-200 shadow-sm">
          {items.length}
        </span>
      </div>
      <div className="flex-1 overflow-auto max-h-[300px] p-0">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-gray-500 uppercase bg-gray-50 sticky top-0">
            <tr>
              <th className="px-4 py-3 font-medium">Employee</th>
              <th className="px-4 py-3 font-medium text-right">
                {type === "probation"
                  ? "End Date"
                  : type === "retirement"
                  ? "DOB"
                  : "Reason"}
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {items.length === 0 ? (
              <tr>
                <td colSpan={2} className="px-4 py-8 text-center text-gray-400">
                  No records found
                </td>
              </tr>
            ) : (
              items.map((item, idx) => (
                <tr key={idx} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900">
                      {item.EMPLOYEE_FULL_NAME}
                    </div>
                    <div className="text-xs text-gray-500">
                      {item.DEPARTMENT_NAME || "N/A"}
                    </div>
                  </td>
                  <td className="px-4 py-3 text-right whitespace-nowrap">
                    {type === "probation" ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-amber-50 text-amber-700">
                        {item.DATE_PROBATION_END
                          ? new Date(item.DATE_PROBATION_END).toLocaleDateString()
                          : "N/A"}
                      </span>
                    ) : type === "retirement" ? (
                      <span className="text-gray-600">
                        {item.DATE_OF_BIRTH
                          ? new Date(item.DATE_OF_BIRTH).toLocaleDateString()
                          : "N/A"}
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-50 text-red-700 max-w-[120px] truncate" title={item.ACTION_REASON}>
                        {item.ACTION_REASON}
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      <div className="p-3 border-t border-gray-100 bg-gray-50/50 rounded-b-xl text-center">
        <Link 
          href={type === "disciplinary" ? "/da-cases" : "/employees"}
          className="text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors block w-full h-full"
        >
          {type === "disciplinary" ? "View DA Dashboard" : "View All"}
        </Link>
      </div>
    </div>
  );
}
