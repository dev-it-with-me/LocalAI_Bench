<script lang="ts">
  import { type TaskResponse, type Category, type ImageInputData, TaskStatusEnum } from '$lib/services/type';

  // Props
  let {
    selectedTask,
    categories,
    onEditTask,
    onDeleteTask
  } = $props<{
    selectedTask: TaskResponse;
    categories: Category[];
    onEditTask: (task: TaskResponse) => void;
    onDeleteTask: (taskId: string) => void;
  }>();
  
  function getCategoryName(categoryId: string): string {
    return categories.find(c => c.id === categoryId)?.name || 'Unknown';
  }

  let hasImages = $derived(
    selectedTask?.input_data?.image && 
    selectedTask.input_data.image.length > 0
  );

  // Status styling based on task status
  const statusStyles = {
    [TaskStatusEnum.DRAFT]: {
      badge: 'bg-amber-500/20 text-amber-300 border border-amber-500/30',
      label: 'Draft'
    },
    [TaskStatusEnum.READY]: {
      badge: 'bg-green-500/20 text-green-300 border border-green-500/30',
      label: 'Ready'
    },
    [TaskStatusEnum.ARCHIVED]: {
      badge: 'bg-gray-500/20 text-gray-300 border border-gray-500/30',
      label: 'Archived'
    }
  };
</script>

<div class="space-y-4">
  {#if selectedTask}
    <div>
      <div class="flex items-center mb-2 gap-2">
        <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium">
          {getCategoryName(selectedTask.category_id)}
        </span>
        <span class="px-2 py-0.5 text-xs rounded-full {statusStyles[selectedTask.status].badge}">
          {statusStyles[selectedTask.status].label}
        </span>
      </div>
      <h3 class="text-lg font-semibold mb-2">{selectedTask.name}</h3>
      <p class="text-surface-200">{selectedTask.description || 'No description'}</p>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <h4 class="font-medium mb-2">Task Input</h4>
      <div class="space-y-3">
        <div>
          <span class="text-sm text-surface-300">User Instruction:</span>
          <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto mt-1">{selectedTask.input_data.user_instruction}</pre>
        </div>
        
        {#if selectedTask.input_data.system_prompt}
          <div>
            <span class="text-sm text-surface-300">System Prompt:</span>
            <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto mt-1">{selectedTask.input_data.system_prompt}</pre>
          </div>
        {/if}
        
        {#if hasImages}
          <div>
            <span class="text-sm text-surface-300">Images:</span>
            <div class="grid grid-cols-3 gap-2 mt-2">
              {#each selectedTask.input_data.image as image}
                <div class="bg-surface-800 p-2 rounded-md">
                  <img 
                    src={image.filepath} 
                    alt={image.filename} 
                    class="h-24 w-full object-cover rounded-md"
                  />
                  <span class="text-xs text-surface-300 truncate block mt-1">{image.filename}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>
    
    <div class="pt-2 border-t border-surface-700">
      <h4 class="font-medium mb-2">Expected Output</h4>
      <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">{selectedTask.expected_output || 'No expected output defined'}</pre>
    </div>
    
    {#if selectedTask.evaluation_weights}
    
      <div class="pt-2 border-t border-surface-700">
        <h4 class="font-medium mb-2">Scoring Weights</h4>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <span class="text-sm text-surface-300">Complexity</span>
            <div class="flex items-center">
              <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                <div class="bg-primary-500 h-full" style="width: {Math.min(selectedTask.evaluation_weights.complexity * 25, 100)}%"></div>
              </div>
              <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.evaluation_weights.complexity}</span>
            </div>
          </div>
          <div>
            <span class="text-sm text-surface-300">Accuracy</span>
            <div class="flex items-center">
              <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                <div class="bg-secondary-500 h-full" style="width: {Math.min(selectedTask.evaluation_weights.accuracy * 25, 100)}%"></div>
              </div>
              <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.evaluation_weights.accuracy}</span>
            </div>
          </div>
          <div>
            <span class="text-sm text-surface-300">Latency</span>
            <div class="flex items-center">
              <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                <div class="bg-success-500 h-full" style="width: {Math.min(selectedTask.evaluation_weights.latency * 25, 100)}%"></div>
              </div>
              <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.evaluation_weights.latency}</span>
            </div>
          </div>
          <div>
            <span class="text-sm text-surface-300">Cost/Memory Usage</span>
            <div class="flex items-center">
              <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                <div class="bg-error-600 h-full" style="width: {Math.min(selectedTask.evaluation_weights.cost_memory_usage * 25, 100)}%"></div>
              </div>
              <span class="ml-2 text-sm min-w-[2rem] text-center">{selectedTask.evaluation_weights.cost_memory_usage}</span>
            </div>
          </div>
        </div>
      </div>
    {/if}
    
    <div class="pt-4 border-t border-surface-700">
      <div class="flex justify-between text-sm text-surface-400">
        <span>Created: {new Date(selectedTask.created_at).toLocaleDateString()}</span>
        <span>Updated: {new Date(selectedTask.updated_at).toLocaleDateString()}</span>
      </div>
    </div>
    
    <div class="flex space-x-2 pt-4">
      <button onclick={() => onEditTask(selectedTask)} class="px-3 py-1 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">Edit</button>
      <button onclick={() => onDeleteTask(selectedTask.id)} class="px-3 py-1 bg-error-500 text-white rounded-md hover:bg-error-600 flex-1">Delete</button>
    </div>
  {/if}
</div>
