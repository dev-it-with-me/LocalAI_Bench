<script lang="ts">
  import type { ModelResponse } from '$lib/services/type';

  // Props
  let { models, selectedModel, onSelectModel, onEditModel, onDeleteModel } = $props<{
    models: ModelResponse[];
    selectedModel: ModelResponse | null;
    onSelectModel: (model: ModelResponse) => void;
    onEditModel: (model: ModelResponse) => void;
    onDeleteModel: (id: string) => void;
  }>();
</script>

<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each models as model}
    <div 
      class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedModel?.id === model.id ? 'border-primary-500 ring-1 ring-primary-500' : ''}"
      onclick={() => onSelectModel(model)}
    >
      <div class="p-4">
        <div class="mb-2">
          <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium">
            {model.type}
          </span>
        </div>
        <h3 class="text-lg font-semibold mb-1">{model.name}</h3>
        <p class="text-surface-300 text-sm line-clamp-2">{model.description || 'No description'}</p>
      </div>
      <div class="bg-surface-700/50 px-4 py-2 flex justify-end space-x-1">
        <button 
          onclick={(e) => {
            e.stopPropagation();
            onEditModel(model);
          }}
          class="p-1.5 hover:bg-surface-600 rounded-md"
          aria-label="Edit model"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
          </svg>
        </button>
        <button 
          onclick={(e) => {
            e.stopPropagation();
            onDeleteModel(model.id);
          }}
          class="p-1.5 hover:bg-surface-600 rounded-md text-red-400" 
          aria-label="Delete model"
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
  {/each}
</div>