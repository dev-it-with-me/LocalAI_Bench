<script lang="ts">
  import { getModels, createModel, updateModel, deleteModel } from '$lib/services/api';
  import AddOllamaModel from '$lib/components/models/AddOllamaModel.svelte';
  import ModelList from '$lib/components/models/ModelList.svelte';
  import ModelDetails from '$lib/components/models/ModelDetails.svelte';
  import type { ModelCreateRequest, ModelResponse, OllamaModelConfig, HuggingFaceModelConfig, CustomApiModelConfig } from '$lib/services/type';
  import { ModelProviderEnum } from '$lib/services/type';
  import { getContext } from 'svelte';

  // Access layout store to update right panel content
  const layout: any = getContext('layout');

  // State management
  let models = $state<ModelResponse[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedModel = $state<ModelResponse | null>(null);
  let isSaving = $state(false);
  
  // Form state
  let editMode = $state(false);

  // Derived state
  let hasModels = $derived(models.length > 0);

  // Update the right panel content whenever selection or edit mode changes
  $effect(() => {
    updateRightPanel();
  });

  async function loadModels() {
    try {
      isLoading = true;
      error = null;
      models = await getModels();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to fetch models';
      console.error('[ModelsPage] Failed to load models:', error);
    } finally {
      isLoading = false;
    }
  }

  // Load initial data
  loadModels();

  function selectModel(model: ModelResponse) {
    selectedModel = model;
    editMode = false;
  }

  function addNewModel() {
    editMode = true;
    selectedModel = null;
  }
  
  function editModel(model: ModelResponse) {
    editMode = true;
    selectedModel = model;
  }
  
  async function deleteModelHandler(modelId: string) {
    if (confirm('Are you sure you want to delete this model?')) {
      try {
        await deleteModel(modelId);
        models = models.filter(m => m.id !== modelId);
        
        if (selectedModel?.id === modelId) {
          selectedModel = null;
          editMode = false;
        }
      } catch (e) {
        const errorMessage = e instanceof Error ? e.message : 'Failed to delete model';
        alert(errorMessage);
        console.error('[ModelsPage] Failed to delete model:', errorMessage);
      }
    }
  }

  async function handleSaveModel(request: ModelCreateRequest) {
    isSaving = true;
    try {
      if (selectedModel) {
        // Update existing model
        const updated = await updateModel(selectedModel.id, {
          name: request.name,
          description: request.description,
          config: request.config
        });
        models = models.map(m => m.id === selectedModel.id ? updated : m);
        selectedModel = updated;
      } else {
        // Add new model
        const created = await createModel(request);
        models = [...models, created];
        selectedModel = created;
      }
      
      editMode = false;
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'Failed to save model';
      alert(errorMessage);
      console.error('[ModelsPage] Failed to save model:', errorMessage);
      throw e; // Re-throw to be handled by the form
    } finally {
      isSaving = false;
    }
  }

  function cancelEdit() {
    editMode = false;
    if (!selectedModel) {
      selectedModel = null;
    }
  }

  function updateRightPanel() {
    if (editMode) {
      // Set form in right panel
      layout.configurationTitle = selectedModel ? `Edit Model: ${selectedModel.name}` : 'Add New Model';
      layout.hasConfigContent = true;
      
      // Set form component
      layout.configContent = () => ({
        component: AddOllamaModel,
        props: {
          model: selectedModel,  // Pass the selected model for editing
          onSubmit: handleSaveModel,
          onCancel: cancelEdit
        }
      });
    } else if (selectedModel) {
      // Set details in right panel
      layout.configurationTitle = `Model: ${selectedModel.name}`;
      layout.hasConfigContent = true;
      
      // Set details component
      layout.configContent = () => ({
        component: ModelDetails,
        props: {
          model: selectedModel,
          onEdit: editModel,
          onDelete: deleteModelHandler
        }
      });
    } else {
      // Clear right panel
      layout.configurationTitle = 'Model Details';
      layout.hasConfigContent = false;
      layout.configContent = null;
    }
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
          loadModels();
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
    <ModelList
      models={models}
      {selectedModel}
      onSelectModel={selectModel}
      onEditModel={editModel}
      onDeleteModel={deleteModelHandler}
    />
  {/if}
</div>