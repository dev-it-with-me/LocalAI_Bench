<script lang="ts">
  // filepath: src/lib/components/categories/CategoryForm.svelte

  // Props
  let {
    selectedCategory,
    formName,
    formDescription,
    isSaving,
    onSaveCategory,
    onCancelEdit,
  } = $props<{ 
    selectedCategory: any;
    formName: string;
    formDescription: string;
    isSaving: boolean;
    onSaveCategory: (data: { name: string; description: string }) => void;
    onCancelEdit: () => void;
  }>();

  let localName = $state(formName);
  let localDescription = $state(formDescription);

  // Update local values when props change
  $effect(() => {
    localName = formName;
    localDescription = formDescription;
  });
</script>

<div class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden">
  <div class="bg-surface-700 px-4 py-3">
    <h2 class="text-lg font-medium">
      {selectedCategory ? 'Edit Category' : 'New Category'}
    </h2>
  </div>

  <div class="p-4">
    <!-- Category Edit Form -->
    <form class="space-y-4">
      <div>
        <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name*</label>
        <input
          id="name"
          type="text"
          bind:value={localName}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
          placeholder="Category name"
          required
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
          onclick={(e) => {
            e.preventDefault();
            onSaveCategory({ name: localName, description: localDescription });
          }}
          disabled={isSaving}
          class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1 flex items-center justify-center"
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
        <button type="button" onclick={onCancelEdit} class="px-4 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1">
          Cancel
        </button>
      </div>
    </form>
  </div>
</div>