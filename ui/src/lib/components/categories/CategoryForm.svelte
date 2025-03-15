<script lang="ts">
  import type { CategoryModel, CategoryCreateRequest, CategoryUpdateRequest } from '$lib/services/type';

  // Props
  let {
    selectedCategory,
    formName,
    formDescription,
    isSaving,
    onSaveCategory,
    onCancelEdit,
  } = $props<{ 
    selectedCategory: CategoryModel | null;
    formName: string;
    formDescription: string;
    isSaving: boolean;
    onSaveCategory: (data: CategoryCreateRequest | CategoryUpdateRequest) => void;
    onCancelEdit: () => void;
  }>();

  let localName = $state(formName);
  let localDescription = $state(formDescription);
  let errorMessage = $state<string | null>(null);

  // Update local values when props change
  $effect(() => {
    localName = formName;
    localDescription = formDescription;
  });

  function validateForm(): boolean {
    errorMessage = null;
    if (!localName.trim()) {
      errorMessage = 'Category name is required';
      return false;
    }
    if (localName.length < 3) {
      errorMessage = 'Category name must be at least 3 characters long';
      return false;
    }
    return true;
  }

  function handleSubmit(e: Event) {
    e.preventDefault();
    if (!validateForm()) return;

    const categoryData = {
      name: localName.trim(),
      description: localDescription.trim()
    };
    
    onSaveCategory(categoryData);
  }
</script>

<div class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden">
  <div class="bg-surface-700 px-4 py-3">
    <h2 class="text-lg font-medium">
      {selectedCategory ? 'Edit Category' : 'New Category'}
    </h2>
  </div>

  <div class="p-4">
    <form class="space-y-4" onsubmit={handleSubmit}>
      {#if errorMessage}
        <div class="bg-red-900/30 border border-red-800 text-red-200 p-3 rounded-md text-sm">
          {errorMessage}
        </div>
      {/if}

      <div>
        <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name*</label>
        <input
          id="name"
          type="text"
          bind:value={localName}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder="Category name"
          required
          minlength="3"
        />
      </div>

      <div>
        <label for="description" class="block text-sm font-medium text-surface-200 mb-1">Description</label>
        <textarea
          id="description"
          rows="3"
          bind:value={localDescription}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder="Category description"
        />
      </div>

      <div class="flex space-x-3 pt-4">
        <button
          type="submit"
          disabled={isSaving}
          class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:bg-primary-500/50 disabled:cursor-not-allowed flex-1 flex items-center justify-center"
        >
          {#if isSaving}
            <svg
              class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          {/if}
          {selectedCategory ? 'Update' : 'Create'} Category
        </button>
        <button 
          type="button" 
          onclick={onCancelEdit} 
          disabled={isSaving}
          class="px-4 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 disabled:bg-surface-600/50 disabled:cursor-not-allowed flex-1"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</div>