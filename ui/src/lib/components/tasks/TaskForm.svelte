<script lang="ts">
  // Props
  let {
    selectedTask,
    formName,
    formDescription,
    formCategoryId,
    formTemplateId,
    formInputData,
    formExpectedOutput,
    formComplexity,
    formAccuracyWeight,
    formLatencyWeight,
    formThroughputWeight,
    formCostWeight,
    categories,
    templates,
    selectedTemplate,
    isSaving,
    onSaveTask,
    onCancelEdit,
    onTemplateChange
  } = $props<{
    selectedTask: any;
    formName: string;
    formDescription: string;
    formCategoryId: string;
    formTemplateId: string;
    formInputData: Record<string, any>;
    formExpectedOutput: Record<string, any>;
    formComplexity: number;
    formAccuracyWeight: number;
    formLatencyWeight: number;
    formThroughputWeight: number;
    formCostWeight: number;
    categories: any[];
    templates: any[];
    selectedTemplate: any;
    isSaving: boolean;
    onSaveTask: (taskData: {
      name: string;
      description: string;
      category_id: string;
      template_id: string;
      input_data: Record<string, any>;
      expected_output: Record<string, any>;
      complexity: number;
      accuracy_weight: number;
      latency_weight: number;
      throughput_weight: number;
      cost_weight: number;
    }) => void;
    onCancelEdit: () => void;
    onTemplateChange: (templateId: string) => void;
  }>();

  function handleJsonInput(value: string, target: 'input' | 'output'): void {
    try {
      const parsed = JSON.parse(value);
      if (target === 'input') {
        formInputData = parsed;
      } else {
        formExpectedOutput = parsed;
      }
    } catch (e) {
      // Invalid JSON, don't update
    }
  }
</script>

<form class="space-y-4" onsubmit={(e) => {
  e.preventDefault(); // Prevent default form submission
  onSaveTask({
    name: formName,
    description: formDescription,
    category_id: formCategoryId,
    template_id: formTemplateId,
    input_data: formInputData,
    expected_output: formExpectedOutput,
    complexity: formComplexity,
    accuracy_weight: formAccuracyWeight,
    latency_weight: formLatencyWeight,
    throughput_weight: formThroughputWeight,
    cost_weight: formCostWeight
  });
}}>
  <div>
    <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name</label>
    <input
      id="name"
      type="text"
      bind:value={formName}
      class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      placeholder="Task name"
      required
    />
  </div>
  
  <div>
    <label for="description" class="block text-sm font-medium text-surface-200 mb-1">Description</label>
    <textarea
      id="description"
      rows="3"
      bind:value={formDescription}
      class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      placeholder="Task description"
      required
    ></textarea>
  </div>
  
  <div class="grid grid-cols-2 gap-4">
    <div>
      <label for="category" class="block text-sm font-medium text-surface-200 mb-1">Category</label>
      <select
        id="category"
        bind:value={formCategoryId}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
        required
      >
        <option value="" disabled={!formCategoryId}>Select category</option>
        {#each categories as category}
          <option value={category.id}>{category.name}</option>
        {/each}
      </select>
    </div>
    
    <div>
      <label for="template" class="block text-sm font-medium text-surface-200 mb-1">Template</label>
      <select
        id="template"
        bind:value={formTemplateId}
        onchange={() => onTemplateChange(formTemplateId)}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
        required
      >
        <option value="" disabled={!formTemplateId}>Select template</option>
        {#each templates as template}
          <option value={template.id}>{template.name}</option>
        {/each}
      </select>
    </div>
  </div>
  
  {#if selectedTemplate}
    <div class="space-y-4 pt-2 border-t border-surface-700">
      <div>
        <label class="block text-sm font-medium text-surface-200 mb-1">Input Data</label>
        <textarea
          rows="8"
          onchange={(e) => handleJsonInput(e.target.value, 'input')}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        >{JSON.stringify(formInputData, null, 2)}</textarea>
        {#if selectedTemplate.input_schema}
          <div class="mt-2 px-3 py-2 bg-surface-800 rounded-md">
            <h4 class="text-xs font-medium text-surface-300 mb-1">Schema:</h4>
            <pre class="text-xs text-surface-300 overflow-x-auto">{JSON.stringify(selectedTemplate.input_schema, null, 2)}</pre>
          </div>
        {/if}
      </div>

      <div>
        <label class="block text-sm font-medium text-surface-200 mb-1">Expected Output</label>
          <textarea
          rows="8"
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
          onchange={(e) => handleJsonInput((e.currentTarget as HTMLTextAreaElement).value, 'output')}
        >{JSON.stringify(formExpectedOutput, null, 2)}</textarea>
        {#if selectedTemplate.output_schema}
          <div class="mt-2 px-3 py-2 bg-surface-800 rounded-md">
            <h4 class="text-xs font-medium text-surface-300 mb-1">Schema:</h4>
            <pre class="text-xs text-surface-300 overflow-x-auto">{JSON.stringify(selectedTemplate.output_schema, null, 2)}</pre>
          </div>
        {/if}
      </div>
    </div>
  {:else}
    <div class="text-sm text-surface-400 italic">Select a template to configure input and output data</div>
  {/if}
  
  
  <div class="space-y-4 pt-2 border-t border-surface-700">
      <h4 class="font-medium">Scoring Weights (0.5 - 4.0)</h4>
      <div>
        <label for="complexity" class="block text-sm font-medium text-surface-200 mb-1">Complexity (0.5 - 4.0)</label>
        <div class="flex items-center">
          <input
            type="range"
            id="complexity"
            min="0.5"
            max="4"
            step="0.1"
            bind:value={formComplexity}
            class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
          />
          <span class="ml-2 text-sm min-w-[2.5rem] text-center">{formComplexity}</span>
        </div>
      </div>
    
    <div>
      <label class="block text-sm font-medium text-surface-200 mb-1">Accuracy Weight</label>
      <div class="flex items-center">
        <input
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={formAccuracyWeight}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{formAccuracyWeight}</span>
      </div>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-surface-200 mb-1">Latency Weight</label>
      <div class="flex items-center">
        <input
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={formLatencyWeight}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{formLatencyWeight}</span>
      </div>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-surface-200 mb-1">Throughput Weight</label>
      <div class="flex items-center">
        <input
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={formThroughputWeight}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{formThroughputWeight}</span>
      </div>
    </div>
    
    <div>
      <label class="block text-sm font-medium text-surface-200 mb-1">Cost Weight</label>
      <div class="flex items-center">
        <input
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={formCostWeight}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{formCostWeight}</span>
      </div>
    </div>
  </div>
  
  <div class="flex space-x-2 pt-4">
    <button
      type="submit"
      disabled={isSaving}
      class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {isSaving ? 'Saving...' : (selectedTask ? 'Update' : 'Create')} Task
    </button>
    <button
      type="button"
      onclick={onCancelEdit}
      disabled={isSaving}
      class="px-3 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      Cancel
    </button>
  </div>
</form>
