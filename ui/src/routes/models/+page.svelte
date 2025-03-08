<script lang="ts">
  import { getModels } from '$lib/services/api';
  
  // Model related types
  type ModelProvider = 'HUGGINGFACE' | 'OLLAMA' | 'CUSTOM_API';

  type Model = {
    id: string;
    name: string;
    description: string;
    provider: ModelProvider;
    config: Record<string, any>;
    created_at: string;
    updated_at: string;
  };

  // Provider-specific config schemas
  const configSchemas = {
    HUGGINGFACE: {
      type: "object",
      properties: {
        model_name: { type: "string" },
        use_gpu: { type: "boolean" },
        max_length: { type: "number" },
        temperature: { type: "number" }
      },
      required: ["model_name"]
    },
    OLLAMA: {
      type: "object",
      properties: {
        model_name: { type: "string" },
        endpoint: { type: "string" },
        parameters: {
          type: "object",
          properties: {
            temperature: { type: "number" },
            top_p: { type: "number" }
          }
        }
      },
      required: ["model_name", "endpoint"]
    },
    CUSTOM_API: {
      type: "object",
      properties: {
        endpoint: { type: "string" },
        headers: { type: "object" },
        prompt_key: { type: "string" },
        response_key: { type: "string" }
      },
      required: ["endpoint", "prompt_key", "response_key"]
    }
  };
  
  // State management using Svelte 5 runes
  let models = $state<Model[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedModel = $state<Model | null>(null);
  
  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let formProvider = $state<ModelProvider>('HUGGINGFACE');
  let formConfig = $state<Record<string, any>>({});
  
  // Right panel state
  let configurationTitle = $state('Model Details');
  let hasConfigContent = $state(false);
  let configContent = $state<any>(null);
  
  // Derived properties
  let hasModels = $derived(models.length > 0);
  let currentSchema = $derived(configSchemas[formProvider]);
  let isValidConfig = $derived(() => {
    try {
      const schema = configSchemas[formProvider];
      const required = schema.required || [];
      return required.every(key => formConfig[key] != null);
    } catch {
      return false;
    }
  });
  
  async function loadModels() {
    try {
      models = await getModels();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to fetch models';
    } finally {
      isLoading = false;
    }
  }

  loadModels();
  
  function selectModel(model: Model) {
    selectedModel = model;
    configurationTitle = `Model: ${model.name}`;
    hasConfigContent = true;
    configContent = ModelDetails;
  }
  
  function addNewModel() {
    editMode = false;
    formName = '';
    formDescription = '';
    formProvider = 'HUGGINGFACE';
    formConfig = {};
    configurationTitle = 'Add New Model';
    hasConfigContent = true;
    configContent = ModelForm;
  }
  
  function editModel(model: Model) {
    editMode = true;
    formName = model.name;
    formDescription = model.description;
    formProvider = model.provider;
    formConfig = { ...model.config };
    configurationTitle = `Edit Model: ${model.name}`;
    hasConfigContent = true;
    configContent = ModelForm;
  }
  
  function deleteModel(modelId: string) {
    if (confirm('Are you sure you want to delete this model?')) {
      // In a real app, delete via API
      models = models.filter(m => m.id !== modelId);
      
      if (selectedModel?.id === modelId) {
        selectedModel = null;
        hasConfigContent = false;
      }
    }
  }
  
  function saveModel() {
    if (!formName.trim()) {
      alert('Model name is required');
      return;
    }
    
    if (!isValidConfig) {
      alert('Please fill in all required configuration fields');
      return;
    }
    
    const now = new Date().toISOString();
    
    if (editMode && selectedModel) {
      // Update existing model
      models = models.map(m => 
        m.id === selectedModel.id 
          ? { 
              ...m, 
              name: formName, 
              description: formDescription,
              provider: formProvider,
              config: formConfig,
              updated_at: now
            } 
          : m
      );
      
      // Update selected model to reflect changes
      selectedModel = models.find(m => m.id === selectedModel?.id) || null;
    } else {
      // Add new model
      const newModel: Model = {
        id: crypto.randomUUID(),
        name: formName,
        description: formDescription,
        provider: formProvider,
        config: formConfig,
        created_at: now,
        updated_at: now
      };
      
      models = [...models, newModel];
      selectedModel = newModel;
    }
    
    // Switch back to model details view
    configurationTitle = `Model: ${selectedModel?.name}`;
    configContent = ModelDetails;
  }
  
  // Model details component for the right panel
  const ModelDetails = {
    render: () => {
      if (!selectedModel) return null;
      
      return `
        <div class="space-y-4">
          <div>
            <div class="mb-2">
              <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium">
                ${selectedModel.provider}
              </span>
            </div>
            <h3 class="text-lg font-semibold mb-2">${selectedModel.name}</h3>
            <p class="text-surface-200">${selectedModel.description || 'No description'}</p>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <h4 class="font-medium mb-2">Configuration</h4>
            <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">${JSON.stringify(selectedModel.config, null, 2)}</pre>
          </div>
          
          <div class="pt-4 border-t border-surface-700">
            <div class="flex justify-between text-sm text-surface-400">
              <span>Created: ${new Date(selectedModel.created_at).toLocaleDateString()}</span>
              <span>Updated: ${new Date(selectedModel.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
          
          <div class="flex space-x-2 pt-4">
            <button onclick=${() => editModel(selectedModel!)} class="px-3 py-1 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">Edit</button>
            <button onclick=${() => deleteModel(selectedModel!.id)} class="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1">Delete</button>
          </div>
        </div>
      `;
    }
  };
  
  // Model form component for the right panel
  const ModelForm = {
    render: () => {
      return `
        <form class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name</label>
            <input
              id="name"
              type="text"
              value="${formName}"
              oninput=${(e: Event) => {
                formName = (e.target as HTMLInputElement).value;
              }}
              class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
              placeholder="Model name"
              required
            />
          </div>
          
          <div>
            <label for="description" class="block text-sm font-medium text-surface-200 mb-1">Description</label>
            <textarea
              id="description"
              rows="3"
              oninput=${(e: Event) => {
                formDescription = (e.target as HTMLTextAreaElement).value;
              }}
              class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
              placeholder="Model description"
            >${formDescription}</textarea>
          </div>
          
          <div>
            <label for="provider" class="block text-sm font-medium text-surface-200 mb-1">Provider</label>
            <select
              id="provider"
              onchange=${(e: Event) => {
                formProvider = (e.target as HTMLSelectElement).value as ModelProvider;
                formConfig = {}; // Reset config when provider changes
              }}
              class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
              required
            >
              ${['HUGGINGFACE', 'OLLAMA', 'CUSTOM_API'].map(provider => 
                `<option value="${provider}" ${formProvider === provider ? 'selected' : ''}>${provider}</option>`
              ).join('')}
            </select>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <h4 class="font-medium mb-2">Configuration</h4>
            ${renderJsonEditor(
              formConfig,
              (value) => { formConfig = value; },
              currentSchema
            )}
          </div>
          
          <div class="flex space-x-2 pt-4">
            <button
              type="submit"
              onclick=${(e: Event) => {
                e.preventDefault();
                saveModel();
              }}
              class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1"
            >
              ${editMode ? 'Update' : 'Create'} Model
            </button>
            <button
              type="button"
              onclick=${() => {
                if (selectedModel) {
                  configContent = ModelDetails;
                  configurationTitle = `Model: ${selectedModel.name}`;
                } else {
                  hasConfigContent = false;
                }
              }}
              class="px-3 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1"
            >
              Cancel
            </button>
          </div>
        </form>
      `;
    }
  };
  
  // Utility function to render JSON editor
  function renderJsonEditor(value: Record<string, any>, onChange: (value: Record<string, any>) => void, schema?: Record<string, any>) {
    const jsonString = JSON.stringify(value, null, 2);
    
    return `
      <div>
        <div class="mb-4">
          <pre class="text-xs text-surface-300 bg-surface-800 p-3 rounded-md overflow-x-auto">
            <div class="font-medium mb-1">Schema:</div>
${JSON.stringify(schema, null, 2)}
          </pre>
        </div>
        <textarea
          rows="10"
          oninput=${(e: Event) => {
            try {
              const newValue = JSON.parse((e.target as HTMLTextAreaElement).value);
              onChange(newValue);
            } catch {
              // Invalid JSON, don't update
            }
          }}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        >${jsonString}</textarea>
      </div>
    `;
  }
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Models</h1>
    <button 
      onclick={addNewModel}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md flex items-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      New Model
    </button>
  </div>
  
  {#if isLoading}
    <div class="flex items-center justify-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
    </div>
  {:else if error}
    <div class="bg-red-900/30 border border-red-800 text-white p-4 rounded-md">
      <h3 class="text-lg font-semibold">Error</h3>
      <p>{error}</p>
      <button 
        class="mt-2 px-4 py-1 bg-red-800 hover:bg-red-700 rounded-md"
        onclick={() => {
          error = null;
          isLoading = true;
          // Retry loading
          setTimeout(() => {
            isLoading = false;
          }, 1000);
        }}
      >
        Retry
      </button>
    </div>
  {:else if !hasModels}
    <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-400 mb-4">
        <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
        <line x1="8" y1="21" x2="16" y2="21"></line>
        <line x1="12" y1="17" x2="12" y2="21"></line>
      </svg>
      <h3 class="text-lg font-semibold mb-2">No Models Found</h3>
      <p class="text-surface-400 mb-4">Configure your first model to start benchmarking</p>
      <button 
        onclick={addNewModel}
        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
      >
        Configure First Model
      </button>
    </div>
  {:else}
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {#each models as model}
        <div 
          class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedModel?.id === model.id ? 'border-primary-500 ring-1 ring-primary-500' : ''}"
          onclick={() => selectModel(model)}
        >
          <div class="p-4">
            <div class="mb-2">
              <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium">
                {model.provider}
              </span>
            </div>
            <h3 class="text-lg font-semibold mb-1">{model.name}</h3>
            <p class="text-surface-300 text-sm line-clamp-2">{model.description || 'No description'}</p>
          </div>
          <div class="bg-surface-700/50 px-4 py-2 flex justify-end space-x-1">
            <button 
              onclick={(e) => {
                e.stopPropagation();
                editModel(model);
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
                deleteModel(model.id);
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
  {/if}
</div>