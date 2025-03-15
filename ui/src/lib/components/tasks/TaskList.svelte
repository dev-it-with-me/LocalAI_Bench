<script lang="ts">
  import TaskListItem from './TaskListItem.svelte';
  import { type TaskResponse, type Category } from '$lib/services/type';

  // Props
  let { tasks, selectedTask, categories, onSelectTask, onEditTask, onDeleteTask } = $props<{
    tasks: TaskResponse[];
    selectedTask: TaskResponse | null;
    categories: Category[];
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
      onSelectTask={onSelectTask}
      onEditTask={onEditTask}
      onDeleteTask={onDeleteTask}
    />
  {/each}
</div>
