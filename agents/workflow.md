**Overall Workflow**

1.  **Feature Request/Refactor Plan:** The human project manager (you) provides a high-level description of the desired feature, refactoring, or bug fix. This description is then written be AI PM to specific format - {task_name/number}.md file.

2.  **Analyst/PM Task:**
    *   The Analyst/PM agent receives the task description from the human project manager.
    *   The Analyst/PM agent creates a "Task Details" file (JSON format).

4.  **Developer Agent Review:**
    *   The Developer agent receives the "Task Details" file.
    *   The Developer agent *thoroughly* reviews the *entire* "Task Details" file *before* writing any code.
    *   If anything is unclear, ambiguous, missing, or inconsistent, the Developer agent *must* request clarification from the Analyst/PM agent *before* proceeding.

6.  **Developer Task Implementation:**
    *   The Developer agent implements the feature, refactor, or bug fix *exactly* as specified in the "Task Details" file.
    *   The Developer agent adheres to strict coding style guidelines

7.  **Integration and Testing:** The human project manager test implemented changes.