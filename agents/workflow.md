**Overall Workflow**

1.  **Feature Request/Refactor Plan:** The human project manager (you) provides a high-level description of the desired feature, refactoring, or bug fix. This description should include:
    *   The goal of the task.
    *   Expected user behavior (if applicable).
    *   Relevant constraints or considerations.
    *   Priority (e.g., "high," "medium," "low").
    *  Any known impacted files or modules (Optional).

2.  **Analyst/PM Task:**
    *   The Analyst/PM agent receives the Feature Request/Refactor Plan.
    *   The Analyst/PM agent reviews the existing codebase.
    *   The Analyst/PM agent creates a "Task Details" file (JSON format).

3.  **"Task Details" File Creation:** (See detailed guidelines for the Analyst/PM agent below).

4.  **Developer Agent Review:**
    *   The Developer agent receives the "Task Details" file.
    *   The Developer agent *thoroughly* reviews the *entire* "Task Details" file *before* writing any code.
    *   If anything is unclear, ambiguous, missing, or inconsistent, the Developer agent *must* request clarification from the Analyst/PM agent *before* proceeding.

5.  **Clarification Loop (if needed):**
    *   The Developer agent sends specific questions or flags issues to the Analyst/PM agent using a standardized JSON format.
    *   The Analyst/PM agent revises the "Task Details" file to address the Developer's concerns.
    *   Steps 4 and 5 repeat until the Developer agent is satisfied that the "Task Details" file is complete and unambiguous.

6.  **Developer Task:**
    *   The Developer agent implements the feature, refactor, or bug fix *exactly* as specified in the "Task Details" file.
    *   The Developer agent adheres to strict coding style guidelines (PEP 8 for Python).
    *   The Developer agent *does not* access the codebase directly; all necessary information is in the "Task Details" file.

7.  **Code Output:** The Developer agent outputs the modified and/or new code files in a specified JSON format (mapping file paths to file contents).

8.  **Integration and Testing:** The human project manager (or another agent/system) integrates the modified code into the main codebase and runs the tests specified in the "Task Details" file (and any existing tests).

9.  **Iteration (if needed):** If tests fail or the implementation doesn't meet the requirements, the process returns to step 2 (Analyst/PM revises the "Task Details" file based on the test results and feedback).
