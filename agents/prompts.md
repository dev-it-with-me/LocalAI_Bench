**I. Initial Feature Request/Refactor Plan for PM Agent**
```
As my Project Manager I want you to prepare a task for the Analyst agent to work on. 
The task should follow the proper format. It should include all necessary data and acceptance criteria.

Task goal is: [Describe the goal of the task in a clear and concise manner.]
```

**II. Preparation of Task Details For Analyst Agent**
```
As my Analyst Agent I want you to create a "Task Details" file for the Developer agent to work on.
The file should include all necessary data and acceptance criteria.
Task is described in the file: {task_name/number}.md
```

**III. Developer Agent Review**
```
As my Developer Agent I want you to review the "Task Details" file created by the Analyst agent.
The file should be reviewed thoroughly before writing any code.
If anything is unclear, ambiguous, missing, or inconsistent, you must request clarification from the Analyst agent before proceeding.
Task details file: {task_name/number}.json

If the file is clear, you can proceed with the implementation.
```