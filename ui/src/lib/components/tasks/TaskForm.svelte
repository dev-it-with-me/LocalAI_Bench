<script lang="ts">
  import { 
    type TaskResponse, 
    type Category, 
    type TaskCreateRequest,
    type TaskUpdateRequest,
    type ImageInputData,
    TaskStatusEnum
  } from '$lib/services/type';
  
  // Props
  let {
    selectedTask,
    formName,
    formDescription,
    formCategoryId,
    formInputData,
    formExpectedOutput,
    formStatus,
    categories,
    isSaving,
    onSaveTask,
    onCancelEdit
  } = $props<{
    selectedTask: TaskResponse | null;
    formName: string;
    formDescription: string;
    formCategoryId: string;
    formInputData: Record<string, any>;
    formExpectedOutput: string | null;
    formStatus: TaskStatusEnum;
    categories: Category[];
    isSaving: boolean;
    onSaveTask: (taskData: TaskCreateRequest | TaskUpdateRequest) => void;
    onCancelEdit: () => void;
  }>();

  // Evaluation weights
  let complexity = $state(selectedTask?.evaluation_weights?.complexity ?? 1.0);
  let accuracy = $state(selectedTask?.evaluation_weights?.accuracy ?? 1.0);
  let latency = $state(selectedTask?.evaluation_weights?.latency ?? 1.0);
  let costMemoryUsage = $state(selectedTask?.evaluation_weights?.cost_memory_usage ?? 1.0);

  // For handling image uploads
  let imageFiles: FileList | null = $state(null);
  let uploadedImages: ImageInputData[] = $state([]);
  
  // Initialize uploadedImages from selectedTask if available
  $effect(() => {
    if (selectedTask?.input_data?.image) {
      uploadedImages = [...selectedTask.input_data.image];
    }
  });

  // Status definitions with colors and labels for UI
  const statusOptions = [
    { value: TaskStatusEnum.DRAFT, label: 'Draft', color: 'bg-amber-500' },
    { value: TaskStatusEnum.READY, label: 'Ready', color: 'bg-green-500' },
    { value: TaskStatusEnum.ARCHIVED, label: 'Archived', color: 'bg-gray-500' }
  ];

  function handleInputDataChange(value: string): void {
    try {
      const parsed = JSON.parse(value);
      // Make sure image field isn't overwritten
      const currentImages = formInputData.image || null;
      formInputData = { ...parsed, image: currentImages };
    } catch (e) {
      // Invalid JSON, don't update
    }
  }
  
  function handleExpectedOutputChange(value: string): void {
    formExpectedOutput = value;
  }

  async function handleImageUpload(): Promise<void> {
    if (!imageFiles || imageFiles.length === 0) return;
    
    // In a real implementation, you would upload the files to your server here
    // and receive back the ImageInputData objects
    // This is a simplified mock implementation
    const newImages: ImageInputData[] = Array.from(imageFiles).map((file, index) => ({
      id: `temp-${Date.now()}-${index}`,
      filename: file.name,
      filepath: URL.createObjectURL(file)
    }));
    
    uploadedImages = [...uploadedImages, ...newImages];
    
    // Update formInputData with the new images
    formInputData = {
      ...formInputData,
      image: uploadedImages
    };
    
    // Clear the file input
    imageFiles = null;
  }
  
  function removeImage(imageId: string): void {
    uploadedImages = uploadedImages.filter(img => img.id !== imageId);
    formInputData = {
      ...formInputData,
      image: uploadedImages.length > 0 ? uploadedImages : null
    };
  }

  function handleSubmit(): void {
    let taskData: TaskCreateRequest | TaskUpdateRequest;
    if (selectedTask) {
      taskData = {
        name: formName,
        description: formDescription,
        category_id: formCategoryId,
        status: formStatus,
        input_data: {
          user_instruction: formInputData.user_instruction || '',
          system_prompt: formInputData.system_prompt || null,
          image: uploadedImages.length > 0 ? uploadedImages : null
        },
        expected_output: formExpectedOutput,
        evaluation_weights: {
          complexity,
          accuracy,
          latency,
          cost_memory_usage: costMemoryUsage
        }
      };
    } else {
      taskData = {
        name: formName,
        description: formDescription,
        category_id: formCategoryId,
        status: formStatus,
        input_data: {
          user_instruction: formInputData.user_instruction || '',
          system_prompt: formInputData.system_prompt || null,
          image: uploadedImages.length > 0 ? uploadedImages : null
        },
        expected_output: formExpectedOutput,
        evaluation_weights: {
          complexity,
          accuracy,
          latency,
          cost_memory_usage: costMemoryUsage
        },
        status: TaskStatusEnum.DRAFT
      };
    }
    
    onSaveTask(taskData);
  }
</script>

<form class="space-y-4" onsubmit={(e) => {
  e.preventDefault();
  handleSubmit();
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
    ></textarea>
  </div>
  
  <div class="flex gap-4">
    <div class="flex-1">
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
    
    <div class="flex-1">
      <label for="status" class="block text-sm font-medium text-surface-200 mb-1">Status</label>
      <select
        id="status"
        bind:value={formStatus}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      >
        {#each statusOptions as status}
          <option value={status.value}>{status.label}</option>
        {/each}
      </select>
    </div>
  </div>
  
  <div class="space-y-4 pt-2 border-t border-surface-700">
    <div>
      <label for="user-instruction" class="block text-sm font-medium text-surface-200 mb-1">User Instruction</label>
      <textarea
        id="user-instruction"
        rows="5"
        bind:value={formInputData.user_instruction}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        placeholder="Enter user instruction"
      ></textarea>
    </div>
    
    <div>
      <label for="system-prompt" class="block text-sm font-medium text-surface-200 mb-1">System Prompt (optional)</label>
      <textarea
        id="system-prompt"
        rows="3"
        bind:value={formInputData.system_prompt}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        placeholder="Enter system prompt"
      ></textarea>
    </div>
    
    <div>
      <label for="image-upload" class="block text-sm font-medium text-surface-200 mb-1">Images (optional)</label>
      <div class="mb-2">
        <input
          type="file"
          id="image-upload"
          accept="image/*"
          multiple
          bind:files={imageFiles}
          class="hidden"
        />
        <div class="flex space-x-2">
          <label for="image-upload" class="px-3 py-1.5 bg-surface-600 text-white rounded-md hover:bg-surface-500 cursor-pointer inline-block">
            Select images
          </label>
          <button
            type="button"
            onclick={handleImageUpload}
            disabled={!imageFiles || imageFiles.length === 0}
            class="px-3 py-1.5 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Upload
          </button>
        </div>
      </div>
      
      {#if uploadedImages.length > 0}
        <div class="grid grid-cols-3 gap-2 mt-4">
          {#each uploadedImages as image}
            <div class="relative group">
              <img 
                src={image.filepath} 
                alt={image.filename} 
                class="h-24 w-full object-cover rounded-md border border-surface-600" 
              />
              <div class="absolute inset-0 flex items-center justify-center bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity rounded-md">
                <button 
                  type="button" 
                  onclick={() => removeImage(image.id)} 
                  class="p-1 bg-red-500 text-white rounded-full hover:bg-red-600"
                  aria-label={`Remove image ${image.filename}`}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
              <span class="text-xs text-surface-300 truncate block mt-1">{image.filename}</span>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <div>
      <label for="expected-output" class="block text-sm font-medium text-surface-200 mb-1">Expected Output</label>
        <textarea
        id="expected-output"
        rows="8"
        bind:value={formExpectedOutput}
        class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        placeholder="Enter expected output"
      ></textarea>
    </div>
  </div>
  
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
            bind:value={complexity}
            class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
          />
          <span class="ml-2 text-sm min-w-[2.5rem] text-center">{complexity}</span>
        </div>
      </div>
    
    <div>
      <label for="accuracy" class="block text-sm font-medium text-surface-200 mb-1">Accuracy Weight</label>
      <div class="flex items-center">
        <input
          id="accuracy"
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={accuracy}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{accuracy}</span>
      </div>
    </div>
    
    <div>
      <label for="latency" class="block text-sm font-medium text-surface-200 mb-1">Latency Weight</label>
      <div class="flex items-center">
        <input
          id="latency"
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={latency}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{latency}</span>
      </div>
    </div>
    
    <div>
      <label for="cost-memory" class="block text-sm font-medium text-surface-200 mb-1">Cost/Memory Usage</label>
      <div class="flex items-center">
        <input
          id="cost-memory"
          type="range"
          min="0.5"
          max="4"
          step="0.1"
          bind:value={costMemoryUsage}
          class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
        />
        <span class="ml-2 text-sm min-w-[2.5rem] text-center">{costMemoryUsage}</span>
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
