<script lang="ts">
  // Props
  let { task, selectedTask, categories, templates, onSelectTask, onEditTask, onDeleteTask } = $props<{
    task: {
      id: string;
      name: string;
      description: string;
      category_id: string;
      template_id: string;
      created_at: string;
      updated_at: string;
    };
    selectedTask: any;
    categories: any[];
    templates: any[];
    onSelectTask: (task: any) => void;
    onEditTask: (task: any) => void;
    onDeleteTask: (taskId: string) => void;
  }>();

  let isSelected = $derived(selectedTask?.id === task.id);
  
  function getCategoryName(categoryId: string): string {
    return categories.find(c => c.id === categoryId)?.name || 'Unknown';
  }
  
  function getTemplateName(templateId: string): string {
    return templates.find(t => t.id === templateId)?.name || 'Unknown';
  }
</script>

<div 
  class="group p-4 bg-surface-800 border border-surface-700 rounded-md cursor-pointer hover:border-primary-500 transition-colors {isSelected ? 'border-primary-500 ring-1 ring-primary-500/30' : ''}"
  onclick={() => onSelectTask(task)}
>
  <div class="flex justify-between items-start mb-2">
    <div>
      <h3 class="font-medium">{task.name}</h3>
      <p class="text-sm text-surface-300 line-clamp-2">{task.description || 'No description'}</p>
    </div>
    <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
      <button
        onclick={(e) => { e.stopPropagation(); onEditTask(task); }}
        class="p-1.5 text-surface-300 hover:text-white hover:bg-surface-700 rounded"
        title="Edit task"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
        </svg>
      </button>
      <button
        onclick={(e) => { e.stopPropagation(); onDeleteTask(task.id); }}
        class="p-1.5 text-surface-300 hover:text-red-400 hover:bg-surface-700 rounded"
        title="Delete task"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
      </button>
    </div>
  </div>
  
  <div class="flex items-center space-x-2 text-xs">
    <span class="px-2 py-0.5 bg-surface-700 rounded text-surface-200">
      {getCategoryName(task.category_id)}
    </span>
    <span class="px-2 py-0.5 bg-primary-900/50 text-primary-200 rounded">
      {getTemplateName(task.template_id)}
    </span>
    <span class="text-surface-400">
      Updated {new Date(task.updated_at).toLocaleDateString()}
    </span>
  </div>
</div>
