"""
Comprehensive integration tests for NLP Query Service
Tests 30+ complex real-world queries against actual database
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.ml.nlp_query_service import NLPQueryService


# Test queries covering all five challenge categories plus extras
TEST_QUERIES = [
    # Location/Department Disambiguation (6 queries)
    {
        "id": 1,
        "query": "How many female employees in the Risk department are based in the UBL Head Office?",
        "expected_sql_contains": ["department", "Risk", "branch_name", "UBL Head Office", "gender"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    {
        "id": 2,
        "query": "Count all employees in UBL Head Office",
        "expected_sql_contains": ["branch_name", "UBL Head Office"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    {
        "id": 3,
        "query": "List employees in Operations department at Karachi branches",
        "expected_sql_contains": ["department", "Operations", "branch_city", "Karachi"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    {
        "id": 4,
        "query": "Show me all departments in UBL Head Office location",
        "expected_sql_contains": ["department", "branch_name", "UBL Head Office"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    {
        "id": 5,
        "query": "How many males work in the Risk department?",
        "expected_sql_contains": ["department", "Risk", "gender"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    {
        "id": 6,
        "query": "Count employees by branch location",
        "expected_sql_contains": ["branch_name", "GROUP BY"],
        "expected_table": "employees",
        "category": "location_dept_disambig"
    },
    
    # Value Normalization - Grades (6 queries)
    {
        "id": 7,
        "query": "Show the average salary for all employees at the avp 1 level",
        "expected_sql_contains": ["grade_level", "AVP-I", "AVG", "salary"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    {
        "id": 8,
        "query": "How many employees are at grade svp 2?",
        "expected_sql_contains": ["grade_level", "SVP-II"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    {
        "id": 9,
        "query": "List all og-3 employees",
        "expected_sql_contains": ["grade_level", "OG-3"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    {
        "id": 10,
        "query": "Count employees by grade level",
        "expected_sql_contains": ["grade_level", "GROUP BY"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    {
        "id": 11,
        "query": "Average performance score for AVP-I grade",
        "expected_sql_contains": ["grade_level", "AVP-I", "performance_score", "AVG"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    {
        "id": 12,
        "query": "Show salary distribution for sc1 grade",
        "expected_sql_contains": ["grade_level", "SC-1", "salary"],
        "expected_table": "employees",
        "category": "grade_normalization"
    },
    
    # Multi-Table ODBC Queries (5 queries)
    {
        "id": 13,
        "query": "List the full name and gross salary for employees who joined before 2020 in the odbc table",
        "expected_sql_contains": ["EMPLOYEE_FULL_NAME", "GROSS_SALARY", "DATE_OF_JOIN", "2020", "odbc"],
        "expected_table": "odbc",
        "category": "odbc_queries"
    },
    {
        "id": 14,
        "query": "Find employees in the North region and flagship branches from ODBC",
        "expected_sql_contains": ["REGION", "North", "BRANCH_FLAGSHIP", "odbc"],
        "expected_table": "odbc",
        "category": "odbc_queries"
    },
    {
        "id": 15,
        "query": "Show all employees with their department name from odbc table",
        "expected_sql_contains": ["DEPARTMENT_NAME", "odbc"],
        "expected_table": "odbc",
        "category": "odbc_queries"
    },
    {
        "id": 16,
        "query": "Count employees by employment status in ODBC",
        "expected_sql_contains": ["EMPLOYMENT_STATUS", "GROUP BY", "odbc"],
        "expected_table": "odbc",
        "category": "odbc_queries"
    },
    {
        "id": 17,
        "query": "List employees with their manager name from odbc",
        "expected_sql_contains": ["MANAGER_EMP_NAME", "odbc"],
        "expected_table": "odbc",
        "category": "odbc_queries"
    },
    
    # Experience & Termination (5 queries)
    {
        "id": 18,
        "query": "Find the employee number and name for everyone with more than 10 years of total experience",
        "expected_sql_contains": ["EMPLOYEE_NUMBER", "Total_Experience", "10", "total_experience"],
        "expected_table": "total_experience",
        "category": "experience"
    },
    {
        "id": 19,
        "query": "Count how many employees have a termination reason related to redundancy",
        "expected_sql_contains": ["ACTION_REASON", "redundancy", "odbc"],
        "expected_table": "odbc",
        "category": "termination"
    },
    {
        "id": 20,
        "query": "Show employees with previous employer information",
        "expected_sql_contains": ["Previous_Employer", "total_experience"],
        "expected_table": "total_experience",
        "category": "experience"
    },
    {
        "id": 21,
        "query": "List terminated employees with their last working date",
        "expected_sql_contains": ["LAST_WORKING_DATE", "odbc"],
        "expected_table": "odbc",
        "category": "termination"
    },
    {
        "id": 22,
        "query": "Count employees by total years of experience ranges",
        "expected_sql_contains": ["Total_Experience", "total_experience"],
        "expected_table": "total_experience",
        "category": "experience"
    },
    
    # Complex Aggregations & Analytics (8 queries)
    {
        "id": 23,
        "query": "What is the average salary by department?",
        "expected_sql_contains": ["AVG", "salary", "department", "GROUP BY"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 24,
        "query": "Show gender distribution by department",
        "expected_sql_contains": ["gender", "department", "GROUP BY"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 25,
        "query": "What is the average performance score by grade level?",
        "expected_sql_contains": ["AVG", "performance_score", "grade_level", "GROUP BY"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 26,
        "query": "Count employees by marital status",
        "expected_sql_contains": ["marital_status", "GROUP BY", "COUNT"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 27,
        "query": "Show salary statistics for each branch city",
        "expected_sql_contains": ["branch_city", "salary", "GROUP BY"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 28,
        "query": "List top 5 departments by employee count",
        "expected_sql_contains": ["department", "COUNT", "GROUP BY", "LIMIT", "5"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 29,
        "query": "Show average years of experience by education level",
        "expected_sql_contains": ["AVG", "years_experience", "education_level", "GROUP BY"],
        "expected_table": "employees",
        "category": "aggregation"
    },
    {
        "id": 30,
        "query": "Count active vs resigned employees",
        "expected_sql_contains": ["status", "GROUP BY", "COUNT"],
        "expected_table": "employees",
        "category": "aggregation"
    },
]


class TestResult:
    def __init__(self, test_id: int, query: str, category: str):
        self.test_id = test_id
        self.query = query
        self.category = category
        self.success = False
        self.generated_sql = ""
        self.execution_success = False
        self.row_count = 0
        self.error = None
        self.validation_notes = []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "query": self.query,
            "category": self.category,
            "success": self.success,
            "generated_sql": self.generated_sql,
            "execution_success": self.execution_success,
            "row_count": self.row_count,
            "error": str(self.error) if self.error else None,
            "validation_notes": self.validation_notes
        }


async def run_comprehensive_tests():
    """Run all test queries and validate results"""
    print("=" * 80)
    print("NLP QUERY SERVICE - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"\nTotal test queries: {len(TEST_QUERIES)}\n")
    
    # Setup database connection
    engine = create_engine(settings.db.SYNC_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    
    results: List[TestResult] = []
    passed = 0
    failed = 0
    
    for test_case in TEST_QUERIES:
        result = TestResult(
            test_id=test_case["id"],
            query=test_case["query"],
            category=test_case["category"]
        )
        
        print(f"\n{'-' * 80}")
        print(f"Test #{test_case['id']}: {test_case['category']}")
        print(f"Query: {test_case['query']}")
        
        try:
            # Create fresh async engine and session for each test to avoid transaction issues
            from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
            async_engine = create_async_engine(
                settings.db.DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            async with AsyncSession(async_engine, expire_on_commit=False) as session:
                try:
                    nlp_service = NLPQueryService(session=session)
                    
                    # Process query
                    response = await nlp_service.process_query(query=test_case["query"])
                    
                    result.generated_sql = response.generated_sql.raw_sql
                    print(f"\n✓ Generated SQL:\n{result.generated_sql}")
                    
                    # Validate SQL content
                    expected_contains = test_case.get("expected_sql_contains", [])
                    sql_lower = result.generated_sql.lower()
                    
                    for expected_term in expected_contains:
                        if expected_term.lower() not in sql_lower:
                            result.validation_notes.append(f"Missing expected term: {expected_term}")
                    
                    # Validate table usage
                    expected_table = test_case.get("expected_table")
                    if expected_table and expected_table.lower() not in sql_lower:
                        result.validation_notes.append(f"Expected table '{expected_table}' not found")
                    
                    # Check if query executed successfully
                    if response.success and response.data is not None:
                        result.execution_success = True
                        result.row_count = len(response.data)
                        print(f"✓ Execution: SUCCESS ({result.row_count} rows)")
                        
                        # Show sample data
                        if result.row_count > 0:
                            print(f"✓ Sample result: {response.data[0]}")
                    else:
                        result.error = response.analysis
                        print(f"✗ Execution: FAILED - {result.error}")
                    
                    # Overall success
                    if result.execution_success and len(result.validation_notes) == 0:
                        result.success = True
                        passed += 1
                        print("✓ PASSED")
                    else:
                        failed += 1
                        print(f"✗ FAILED - {', '.join(result.validation_notes) if result.validation_notes else 'Execution error'}")
                
                except Exception as session_error:
                    # Rollback on any error within the session
                    await session.rollback()
                    raise session_error
                    
            # Dispose of engine after each test
            await async_engine.dispose()
                    
        except Exception as e:
            result.error = str(e)
            failed += 1
            print(f"✗ ERROR: {e}")
        
        results.append(result)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"\nTotal: {len(TEST_QUERIES)}")
    print(f"Passed: {passed} ({100*passed//len(TEST_QUERIES)}%)")
    print(f"Failed: {failed} ({100*failed//len(TEST_QUERIES)}%)")
    
    # Category breakdown
    categories = {}
    for result in results:
        if result.category not in categories:
            categories[result.category] = {"passed": 0, "failed": 0}
        if result.success:
            categories[result.category]["passed"] += 1
        else:
            categories[result.category]["failed"] += 1
    
    print("\nResults by Category:")
    for cat, counts in categories.items():
        total = counts["passed"] + counts["failed"]
        pct = 100 * counts["passed"] // total if total > 0 else 0
        print(f"  {cat}: {counts['passed']}/{total} ({pct}%)")
    
    # Failed tests detail
    if failed > 0:
        print("\n" + "=" * 80)
        print("FAILED TESTS DETAIL")
        print("=" * 80)
        for result in results:
            if not result.success:
                print(f"\nTest #{result.test_id}: {result.query}")
                print(f"  Category: {result.category}")
                print(f"  SQL: {result.generated_sql}")
                print(f"  Error: {result.error}")
                print(f"  Notes: {', '.join(result.validation_notes)}")
    
    # Save detailed results
    import json
    output_file = Path(__file__).parent / "test_results.json"
    with open(output_file, "w") as f:
        json.dump([r.to_dict() for r in results], f, indent=2)
    print(f"\n✓ Detailed results saved to: {output_file}")
    
    return passed == len(TEST_QUERIES)


if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_tests())
    sys.exit(0 if success else 1)
