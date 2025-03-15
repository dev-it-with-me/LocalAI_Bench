<script lang="ts">
  import type { CategoryModel } from '$lib/services/type';

  // Props
  let {
    selectedCategory,
    onEditCategory,
    onDeleteCategory,
    onAddNewCategory,
  } = $props<{ 
    selectedCategory: CategoryModel | null;
    onEditCategory: (category: CategoryModel) => void;
    onDeleteCategory: (categoryId: string) => void;
    onAddNewCategory: () => void;
  }>();
</script>

<div class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden">
  <div class="bg-surface-700 px-4 py-3">
    <h2 class="text-lg font-medium">
      {#if selectedCategory}
        Category Details
      {:else}
        Select a Category
      {/if}
    </h2>
  </div>

  <div class="p-4">
    {#if selectedCategory}
      <!-- Category Details View -->
      <div class="space-y-4">
        <div>
          <h3 class="text-lg font-semibold mb-2">{selectedCategory.name}</h3>
          <p class="text-surface-300">{selectedCategory.description || 'No description'}</p>
        </div>

        <div class="pt-4 border-t border-surface-700">
          <div class="flex justify-between text-sm text-surface-400 mb-2">
            <span>Tasks in category: {selectedCategory.task_ids?.length || 0}</span>
          </div>
          <div class="flex justify-between text-sm text-surface-400">
            <span>Created: {new Date(selectedCategory.created_at).toLocaleDateString()}</span>
            <span>Updated: {new Date(selectedCategory.updated_at).toLocaleDateString()}</span>
          </div>
        </div>

        <div class="flex space-x-2 pt-4">
          <button onclick={() => onEditCategory(selectedCategory)} class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">
            Edit
          </button>
          <button
            onclick={() => {
              if (selectedCategory) onDeleteCategory(selectedCategory.id);
            }}
            class="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1"
          >
            Delete
          </button>
        </div>
      </div>
    {:else}
      <!-- No category selected -->
      <div class="text-center py-8">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1"
          stroke-linecap="round"
          stroke-linejoin="round"
          class="mx-auto text-surface-500 mb-4"
        >
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="16" y1="13" x2="8" y2="13" />
          <line x1="16" y1="17" x2="8" y2="17" />
          <line x1="10" y1="9" x2="8" y2="9" />
        </svg>
        <p class="text-surface-400 mb-4">
          Select a category to view details
          <br />
          or create a new one
        </p>
        <button onclick={onAddNewCategory} class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md">
          Create Category
        </button>
      </div>
    {/if}
  </div>
</div>