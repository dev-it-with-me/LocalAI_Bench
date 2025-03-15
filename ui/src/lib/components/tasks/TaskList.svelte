<script lang="ts">
  import TaskListItem from './TaskListItem.svelte';

  // Props
  let { tasks, selectedTask, categories, templates, onSelectTask, onEditTask, onDeleteTask } = $props<{
    tasks: any[];
    selectedTask: any;
    categories: any[];
    templates: any[];
    onSelectTask: (task: any) => void;
    onEditTask: (task: any) => void;
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
