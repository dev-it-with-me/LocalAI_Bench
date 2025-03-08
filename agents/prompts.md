**I. Initial Feature Request/Refactor Plan**

**Template Prompt:**

```
I need you to [develop a new feature / refactor existing code / fix a bug].

**Goal:** [Clearly state the objective of the task. What should the system do (or stop doing) after this change?]

**Description:** [Provide a detailed description of the feature, refactoring, or bug. Include as much context as possible.]

**User Story (if applicable):** As a [user role], I want [functionality] so that [benefit].

**Acceptance Criteria:** [List specific, measurable, achievable, relevant, and time-bound (SMART) criteria that define when the task is complete. These will be used for testing.]

**Example (for a new feature):**

*   "The user should be able to see a list of all their completed benchmarks."
*   "The list should be sortable by completion date."
*   "Each item in the list should display the benchmark name, completion date, and overall score."
*   "The list should be accessible from the main dashboard."

**Example (for a refactor):**

*   "The `BenchmarkEngine` class is becoming too large and complex.  It should be refactored into smaller, more manageable classes."
*   "The refactoring should not change the existing functionality of the benchmark engine."
*   "The refactored code should be well-documented and easy to understand."
*  "Improve test coverage"

**Example (for a bug fix):**

*   "When a user tries to start a benchmark with no selected models, the application crashes with a `TypeError`."
*   "The application should display a user-friendly error message instead of crashing."
*   "The error message should explain that at least one model must be selected."

**Known Impacted Files/Modules (Optional):** [If you already have a good idea of which parts of the codebase will be affected, list them here. This can help the Analyst/PM get started, but it's *not* required. The Analyst/PM is still responsible for a full analysis.]

**Priority:** [High/Medium/Low]

**Constraints/Considerations:** [Note any specific limitations, technical requirements, or design considerations. This helps the analyst to understand limitations.]
*  Example: The implementation should minimize database queries for performance.
*  Example: This feature must be backwards compatible with existing data.
```

**When to Use:** At the very beginning of a new task (feature, refactor, bug fix).

**Key Points:**

*   **Be as clear and specific as possible.** Ambiguity here will lead to problems down the line.
*   **Focus on the "what," not the "how."** Let the Analyst/PM figure out the implementation details.
*   **Acceptance Criteria are crucial.** They define when the task is truly complete.
* The prompt should be understandable by Analyst.
* Provide all necessary data

**II. Clarification Requests**

**Template Prompt:**

```
Regarding Task ID: [Paste the `task_id` from the Developer's question]

Developer's Question: [Paste the Developer's question verbatim]

My Clarification: [Provide a clear, concise, and unambiguous answer to the Developer's question.  Be as specific as possible.]

**Example:**
Regarding the request for data types, you should add this to the task file:
```json
"data_types": [
    {
        "name": "BenchmarkResult",
        "type": "pydantic_model",
        "fields": [
            { "name": "benchmark_id", "type": "str", "constraints": ["required"] },
            { "name": "model_id", "type": "str", "constraints": ["required"] },
            { "name": "results", "type": "dict", "constraints": ["required"] }
        ]
    }
] 

```
**When to Use:**  In response to a clarification request from the Developer agent.

**Key Points:**

*   **Always reference the `task_id`.** This ensures that the clarification is associated with the correct task.
*   **Quote the Developer's question directly.** This avoids any misinterpretation of the question.
*   **Be extremely precise in your answer.** Avoid ambiguity.
*   **Update the Task Details File:** *Crucially*, after providing clarification, *you* (or another human) must update the "Task Details" file to reflect the clarification.  The Analyst/PM agent should *not* be expected to remember the clarification from a separate communication. The "Task Details" file *must* remain the single source of truth. This might involve you manually editing the JSON, or you might have a tool to help with this.
