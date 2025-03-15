<script lang="ts">
  import type { ModelResponse } from '$lib/services/type';

  const props = $props<{
    model: ModelResponse;
    onEdit: (model: ModelResponse) => void;
    onDelete: (id: string) => void;
  }>();
</script>

<div class="space-y-4">
  <div>
    <div class="mb-2">
      <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium">
        {props.model.provider}
      </span>
    </div>
    <h3 class="text-lg font-semibold mb-2">{props.model.name}</h3>
    <p class="text-surface-200">{props.model.description || 'No description'}</p>
  </div>
  
  <div class="pt-2 border-t border-surface-700">
    <h4 class="font-medium mb-2">Configuration</h4>
    <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">{JSON.stringify(props.model.config, null, 2)}</pre>
  </div>
  
  <div class="pt-4 border-t border-surface-700">
    <div class="flex justify-between text-sm text-surface-400">
      <span>Created: {new Date(props.model.created_at).toLocaleDateString()}</span>
      <span>Updated: {new Date(props.model.updated_at).toLocaleDateString()}</span>
    </div>
  </div>
  
  <div class="flex space-x-2 pt-4">
    <button 
      onclick={() => props.onEdit(props.model)}
      class="px-3 py-1 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1"
    >
      Edit
    </button>
    <button 
      onclick={() => props.onDelete(props.model.id)}
      class="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1"
    >
      Delete
    </button>
  </div>
</div>