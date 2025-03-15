<script lang="ts">
  // Props
  let {
    selectedTask,
    selectedTemplate,
    categories,
    templates,
    onEditTask,
    onDeleteTask
  } = $props<{
    selectedTask: any;
    selectedTemplate: any;
    categories: any[];
    templates: any[];
    onEditTask: (task: any) => void;
    onDeleteTask: (taskId: string) => void;
  }>();
  
  function getCategoryName(categoryId: string): string {
    return categories.find(c => c.id === categoryId)?.name || 'Unknown';
  }
  
  function getTemplateName(templateId: string): string {
    return templates.find(t => t.id === templateId)?.name || 'Unknown';
  }
</script>

<div class="space-y-4">
  {#if selectedTask}
    <div>
      <div class="flex items-center mb-2">
        <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium mr-2">
          {getCategoryName(selectedTask.category_id)}
        </span>
        <span class="px-2 py-0.5 bg-primary-900/50 text-primary-200 rounded text-xs font-medium">
          {getTemplateName(selectedTask.template_id)}
        </span>
      </div>
      <h3 class="text-lg font-semibold mb-2">{selectedTask.name}</h3>
      <p class="text-surface-200">{selectedTask.description || 'No description'}</p>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <h4 class="font-medium mb-2">Task Input</h4>
      <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">{JSON.stringify(selectedTask.input_data, null, 2)}</pre>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <h4 class="font-medium mb-2">Expected Output</h4>
      <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">{JSON.stringify(selectedTask.expected_output, null, 2)}</pre>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <div class="flex justify-between items-center mb-2">
        <span class="text-surface-300">Complexity</span>
        <span class="font-medium">{selectedTask.complexity}</span>
      </div>
      <div class="h-2 bg-surface-700 rounded-full overflow-hidden">
        <div class="bg-primary-500 h-full" style="width: {Math.min(selectedTask.complexity * 25, 100)}%"></div>
      </div>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <h4 class="font-medium mb-2">Scoring Weights</h4>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <span class="text-sm text-surface-300">Accuracy</span>
          <div class="flex items-center">
            <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
              <div class="bg-green-500 h-full" style="width: {Math.min(selectedTask.accuracy_weight * 25, 100)}%"></div>
            </div>
            <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.accuracy_weight}</span>
          </div>
        </div>
        <div>
          <span class="text-sm text-surface-300">Latency</span>
          <div class="flex items-center">
            <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
              <div class="bg-blue-500 h-full" style="width: {Math.min(selectedTask.latency_weight * 25, 100)}%"></div>
            </div>
            <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.latency_weight}</span>
          </div>
        </div>
        <div>
          <span class="text-sm text-surface-300">Throughput</span>
          <div class="flex items-center">
            <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
              <div class="bg-yellow-500 h-full" style="width: {Math.min(selectedTask.throughput_weight * 25, 100)}%"></div>
            </div>
            <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.throughput_weight}</span>
          </div>
        </div>
        <div>
          <span class="text-sm text-surface-300">Cost</span>
          <div class="flex items-center">
            <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
              <div class="bg-red-500 h-full" style="width: {Math.min(selectedTask.cost_weight * 25, 100)}%"></div>
            </div>
            <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.cost_weight}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="pt-4 border-t border-surface-700">
      <div class="flex justify-between text-sm text-surface-400">
        <span>Created: {new Date(selectedTask.created_at).toLocaleDateString()}</span>
        <span>Updated: {new Date(selectedTask.updated_at).toLocaleDateString()}</span>
      </div>
    </div>
    
    <div class="flex space-x-2 pt-4">
      <button onclick={() => onEditTask(selectedTask)} class="px-3 py-1 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">Edit</button>
      <button onclick={() => onDeleteTask(selectedTask.id)} class="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1">Delete</button>
    </div>
  {/if}
</div>
