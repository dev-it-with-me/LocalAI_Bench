<script lang="ts">
  import TaskListItem from './TaskListItem.svelte';
  import { type TaskResponse, type Category, type Template } from '$lib/services/type';

  // Props
  let { tasks, selectedTask, categories, templates, onSelectTask, onEditTask, onDeleteTask } = $props<{
    tasks: TaskResponse[];
    selectedTask: TaskResponse | null;
    categories: Category[];
    templates: Template[];
    onSelectTask: (task: TaskResponse) => void;
    onEditTask: (task: TaskResponse) => void;
    onDeleteTask: (taskId: string) => void;
  }>();
</script>

<div class="space-y-3">
  {#each tasks as task}
    <TaskListItem 
      {task}
      {selectedTask}
      {categories}
      {templates}
      onSelectTask={onSelectTask}
      onEditTask={onEditTask}
      onDeleteTask={onDeleteTask}
    />
  {/each}
</div>
