<script lang="ts">
  // filepath: src/lib/components/categories/CategoryList.svelte
  
  // Props
  let {
    categories,
    selectedCategory,
    onSelectCategory,
    onEditCategory,
    onDeleteCategory,
    onAddNewCategory,
  } = $props<{ 
    categories: any[];
    selectedCategory: any;
    onSelectCategory: (category: any) => void;
    onEditCategory: (category: any) => void;
    onDeleteCategory: (categoryId: string) => void;
    onAddNewCategory: () => void;
  }>();

  let hasCategories = $derived(categories.length > 0);
</script>

{#if !hasCategories}
  <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
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
      class="mx-auto text-surface-400 mb-4"
    >
      <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" />
    </svg>
    <h3 class="text-lg font-semibold mb-2">No Categories Found</h3>
    <p class="text-surface-400 mb-4">Create your first category to organize benchmark tasks</p>
    <button onclick={onAddNewCategory} class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md">
      Create First Category
    </button>
  </div>
{:else}
  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    {#each categories as category}
      <div
        class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedCategory?.id === category.id
          ? 'border-primary-500 ring-1 ring-primary-500'
          : ''}"
        onclick={() => onSelectCategory(category)}
      >
        <div class="p-4">
          <h3 class="text-lg font-semibold mb-1">{category.name}</h3>
          <p class="text-surface-300 text-sm line-clamp-2">{category.description || 'No description'}</p>
        </div>
        <div class="bg-surface-700/50 px-4 py-2 flex justify-between items-center">
          <div class="flex items-center">
            <span class="text-sm text-surface-300 mr-1">Tasks:</span>
            <span class="text-sm font-medium">{category.task_ids?.length || 0}</span>
          </div>
          <div class="flex space-x-1">
            <button
              onclick={(e) => {
                e.stopPropagation();
                onSelectCategory(category);
                onEditCategory(category);
              }}
              class="p-1.5 hover:bg-surface-600 rounded-md" aria-label="Edit category"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </button>
            <button
              onclick={(e) => {
                e.stopPropagation();
                onDeleteCategory(category.id);
              }}
              class="p-1.5 hover:bg-surface-600 rounded-md text-red-400" aria-label="Delete category"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}