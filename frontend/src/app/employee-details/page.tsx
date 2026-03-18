import { getEmployeesBySubGroup } from "@/app/actions/analytics";
import { EmployeeListContent } from "@/components/employees/employee-list-content";

export const dynamic = "force-dynamic";

interface EmployeeDetailsPageProps {
  searchParams: {
    dept_group?: string;
    sub_group?: string;
  };
}

export default async function EmployeeDetailsPage({ searchParams }: EmployeeDetailsPageProps) {
  const { dept_group, sub_group } = searchParams;

  if (!dept_group || !sub_group) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold">Employee Details</h1>
        <p className="text-muted-foreground mt-2">Please select a sub-group from the analytics page.</p>
      </div>
    );
  }

  const employees = await getEmployeesBySubGroup(dept_group, sub_group);

  return (
    <EmployeeListContent
      employees={employees}
      deptGroup={dept_group}
      subGroup={sub_group}
    />
  );
}
