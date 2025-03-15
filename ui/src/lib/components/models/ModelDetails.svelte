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
        {props.model.type}
      </span>
    </div>
    <h3 class="text-lg font-semibold mb-2">{props.model.name}</h3>
    <p class="text-surface-200">{props.model.description || 'No description'}</p>
  </div>
  
  <div class="pt-2 border-t border-surface-700">
    <h4 class="font-medium mb-2">Model Configuration</h4>
    <div class="space-y-2">
      <div>
        <span class="text-sm text-surface-300">Model ID:</span>
        <span class="text-sm ml-2">{props.model.model_id}</span>
      </div>
      <div>
        <span class="text-sm text-surface-300">API URL:</span>
        <span class="text-sm ml-2">{props.model.api_url || 'Not set'}</span>
      </div>
      {#if props.model.parameters}
        <div>
          <span class="text-sm font-medium text-surface-200">Parameters:</span>
          <div class="mt-2 grid grid-cols-2 gap-2">
            {#if props.model.parameters.temperature !== null}
              <div>
                <span class="text-sm text-surface-300">Temperature:</span>
                <span class="text-sm ml-2">{props.model.parameters.temperature}</span>
              </div>
            {/if}
            {#if props.model.parameters.top_p !== null}
              <div>
                <span class="text-sm text-surface-300">Top P:</span>
                <span class="text-sm ml-2">{props.model.parameters.top_p}</span>
              </div>
            {/if}
            {#if props.model.parameters.top_k !== null}
              <div>
                <span class="text-sm text-surface-300">Top K:</span>
                <span class="text-sm ml-2">{props.model.parameters.top_k}</span>
              </div>
            {/if}
            {#if props.model.parameters.max_tokens !== null}
              <div>
                <span class="text-sm text-surface-300">Max Tokens:</span>
                <span class="text-sm ml-2">{props.model.parameters.max_tokens}</span>
              </div>
            {/if}
          </div>
          {#if props.model.parameters.stop_sequences?.length}
            <div class="mt-2">
              <span class="text-sm text-surface-300">Stop Sequences:</span>
              <pre class="mt-1 text-sm bg-surface-800 p-2 rounded">{JSON.stringify(props.model.parameters.stop_sequences, null, 2)}</pre>
            </div>
          {/if}
        </div>
      {/if}
    </div>
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