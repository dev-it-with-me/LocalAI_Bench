<script lang="ts">
  import type { ModelCreateRequest } from '$lib/services/type';
  import { ModelProviderEnum } from '$lib/services/type';

  // Props definition using Svelte 5 runes
  const props = $props<{
    onSubmit: (request: ModelCreateRequest) => Promise<void>;
    onCancel: () => void;
  }>();

  // Form state
  let formState = $state<{
    name: string;
    description: string;
    config: {
      model_id: string;
      host: string;
      temperature: number;
      top_p: number;
      top_k: number;
      max_tokens: number;
      stop_sequences: string[];
    };
  }>({
    name: '',
    description: '',
    config: {
      model_id: '',
      host: 'http://localhost:11434',
      temperature: 0.7,
      top_p: 1.0,
      top_k: 40,
      max_tokens: 2048,
      stop_sequences: []
    }
  });

  // Validation state
  let errors = $state<Partial<Record<keyof typeof formState.config | 'name', string | null>>>({});
  let isSubmitting = $state(false);
  let submitError = $state<string | null>(null);

  // Derived validation state
  let isValid = $derived(
    formState.name.trim() !== '' &&
    formState.config.model_id.trim() !== '' &&
    formState.config.host.trim() !== '' &&
    formState.config.temperature >= 0 && formState.config.temperature <= 2 &&
    formState.config.top_p >= 0 && formState.config.top_p <= 1 &&
    formState.config.top_k >= 1 && formState.config.top_k <= 40 &&
    formState.config.max_tokens >= 1 && formState.config.max_tokens <= 2048
  );

  // Validate individual fields
  function validateField(field: keyof typeof formState.config | 'name', value: any) {
    switch (field) {
      case 'name':
        errors[field] = !value.trim() ? 'Name is required' : null;
        break;
      case 'model_id':
        errors[field] = !value.trim() ? 'Model ID is required' : null;
        break;
      case 'host':
        errors[field] = !value.trim() ? 'Host is required' : null;
        break;
      case 'temperature':
        errors[field] = value < 0 || value > 2 ? 'Temperature must be between 0 and 2' : null;
        break;
      case 'top_p':
        errors[field] = value < 0 || value > 1 ? 'Top P must be between 0 and 1' : null;
        break;
      case 'top_k':
        errors[field] = value < 1 || value > 40 ? 'Top K must be between 1 and 40' : null;
        break;
      case 'max_tokens':
        errors[field] = value < 1 || value > 2048 ? 'Max tokens must be between 1 and 2048' : null;
        break;
    }
  }

  // Handle form submission
  async function handleSubmit(e: Event) {
    e.preventDefault();
    
    // Validate all fields
    validateField('name', formState.name);
    Object.keys(formState.config).forEach(key => {
      validateField(key as keyof typeof formState.config, formState.config[key as keyof typeof formState.config]);
    });
    
    if (!isValid) {
      return;
    }

    try {
      isSubmitting = true;
      submitError = null;

      const request: ModelCreateRequest = {
        name: formState.name,
        description: formState.description,
        provider: ModelProviderEnum.OLLAMA,
        config: formState.config
      };
      
      await props.onSubmit(request);
      
    } catch (error) {
      console.error('[AddOllamaModel] Form submission failed', {
        error: error instanceof Error ? error.message : 'Unknown error',
        formData: formState
      });
      submitError = error instanceof Error ? error.message : 'Failed to add model';
    } finally {
      isSubmitting = false;
    }
  }

  // Handle stop sequences input
  function handleStopSequencesInput(value: string) {
    try {
      formState.config.stop_sequences = JSON.parse(value);
      errors.stop_sequences = null;
    } catch {
      errors.stop_sequences = 'Invalid JSON array format';
    }
  }

  // Handle input blur for validation
  function handleBlur(field: keyof typeof formState.config | 'name') {
    if (field === 'name') {
      validateField(field, formState.name);
    } else {
      validateField(field, formState.config[field]);
    }
  }
</script>

<form onsubmit={handleSubmit} class="space-y-6">
  <div>
    <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name</label>
    <input
      id="name"
      type="text"
      bind:value={formState.name}
      onblur={() => handleBlur('name')}
      class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      placeholder="My Ollama Model"
      required
    />
    {#if errors.name}
      <p class="mt-1 text-sm text-red-500">{errors.name}</p>
    {/if}
  </div>

  <div>
    <label for="description" class="block text-sm font-medium text-surface-200 mb-1">Description</label>
    <textarea
      id="description"
      bind:value={formState.description}
      class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      placeholder="Optional description of your model"
      rows="2"
    ></textarea>
  </div>

  <div class="border-t border-surface-600 pt-6">
    <h3 class="text-lg font-medium mb-4">Model Configuration</h3>
    
    <div class="space-y-4">
      <div>
        <label for="model_id" class="block text-sm font-medium text-surface-200 mb-1">Model ID</label>
        <input
          id="model_id"
          type="text"
          bind:value={formState.config.model_id}
          onblur={() => handleBlur('model_id')}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder="llama2, mistral, etc."
          required
        />
        {#if errors.model_id}
          <p class="mt-1 text-sm text-red-500">{errors.model_id}</p>
        {/if}
      </div>

      <div>
        <label for="host" class="block text-sm font-medium text-surface-200 mb-1">Host</label>
        <input
          id="host"
          type="text"
          bind:value={formState.config.host}
          onblur={() => handleBlur('host')}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder="http://localhost:11434"
          required
        />
        {#if errors.host}
          <p class="mt-1 text-sm text-red-500">{errors.host}</p>
        {/if}
      </div>

      <div class="grid grid-cols-2 gap-4">
        <div>
          <label for="temperature" class="block text-sm font-medium text-surface-200 mb-1">Temperature</label>
          <input
            id="temperature"
            type="number"
            bind:value={formState.config.temperature}
            onblur={() => handleBlur('temperature')}
            class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
            min="0"
            max="2"
            step="0.1"
          />
          {#if errors.temperature}
            <p class="mt-1 text-sm text-red-500">{errors.temperature}</p>
          {/if}
        </div>

        <div>
          <label for="top_p" class="block text-sm font-medium text-surface-200 mb-1">Top P</label>
          <input
            id="top_p"
            type="number"
            bind:value={formState.config.top_p}
            onblur={() => handleBlur('top_p')}
            class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
            min="0"
            max="1"
            step="0.1"
          />
          {#if errors.top_p}
            <p class="mt-1 text-sm text-red-500">{errors.top_p}</p>
          {/if}
        </div>

        <div>
          <label for="top_k" class="block text-sm font-medium text-surface-200 mb-1">Top K</label>
          <input
            id="top_k"
            type="number"
            bind:value={formState.config.top_k}
            onblur={() => handleBlur('top_k')}
            class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
            min="1"
            max="40"
          />
          {#if errors.top_k}
            <p class="mt-1 text-sm text-red-500">{errors.top_k}</p>
          {/if}
        </div>

        <div>
          <label for="max_tokens" class="block text-sm font-medium text-surface-200 mb-1">Max Tokens</label>
          <input
            id="max_tokens"
            type="number"
            bind:value={formState.config.max_tokens}
            onblur={() => handleBlur('max_tokens')}
            class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
            min="1"
            max="2048"
          />
          {#if errors.max_tokens}
            <p class="mt-1 text-sm text-red-500">{errors.max_tokens}</p>
          {/if}
        </div>
      </div>

      <div>
        <label for="stop_sequences" class="block text-sm font-medium text-surface-200 mb-1">Stop Sequences (JSON array)</label>
        <input
          id="stop_sequences"
          type="text"
          value={JSON.stringify(formState.config.stop_sequences)}
          oninput={(e) => handleStopSequencesInput(e.currentTarget.value)}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder='["END", "STOP"]'
        />
        {#if errors.stop_sequences}
          <p class="mt-1 text-sm text-red-500">{errors.stop_sequences}</p>
        {/if}
      </div>
    </div>
  </div>

  {#if submitError}
    <div class="bg-red-900/30 border border-red-800 text-white p-4 rounded-md">
      {submitError}
    </div>
  {/if}

  <div class="flex space-x-2 pt-4">
    <button
      type="submit"
      disabled={!isValid || isSubmitting}
      class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex-1"
    >
      {#if isSubmitting}
        <span class="inline-block animate-spin mr-2">⟳</span>
      {/if}
      Save Model
    </button>
    <button
      type="button"
      onclick={props.onCancel}
      class="px-4 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1"
    >
      Cancel
    </button>
  </div>
</form>