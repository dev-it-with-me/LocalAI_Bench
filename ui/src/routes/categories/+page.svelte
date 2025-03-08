<script lang="ts">
  import { 
    getCategories, 
    createCategory, 
    updateCategory, 
    deleteCategory 
  } from '$lib/services/api';
  
  // Category model type
  type Category = {
    id: string;
    name: string;
    description: string;
    task_ids: string[];
    created_at: string;
    updated_at: string;
  };
  
  // State management using Svelte 5 runes
  let categories = $state<Category[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedCategory = $state<Category | null>(null);
  
  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let isSaving = $state(false);
  
  // Derived properties
  let hasCategories = $derived(categories.length > 0);
  
  async function loadCategories() {
    try {
      isLoading = true;
      error = null;
      categories = await getCategories();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to fetch categories';
    } finally {
      isLoading = false;
    }
  }
  
  // Load categories on page load
  loadCategories();
  
  function selectCategory(category: Category) {
    selectedCategory = category;
    editMode = false;
  }
  
  function addNewCategory() {
    selectedCategory = null;
    editMode = true;
    formName = '';
    formDescription = '';
  }
  
  function editSelectedCategory() {
    if (!selectedCategory) return;
    
    editMode = true;
    formName = selectedCategory.name;
    formDescription = selectedCategory.description;
  }
  
  async function handleDeleteCategory(categoryId: string) {
    if (!confirm('Are you sure you want to delete this category?')) {
      return;
    }
    
    try {
      await deleteCategory(categoryId);
      
      // Remove from local state
      categories = categories.filter(c => c.id !== categoryId);
      
      // Reset selection if deleted category was selected
      if (selectedCategory?.id === categoryId) {
        selectedCategory = null;
        editMode = false;
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete category');
    }
  }
  
  async function saveCategory() {
    // Basic validation
    if (!formName.trim()) {
      alert('Category name is required');
      return;
    }
    
    try {
      isSaving = true;
      
      const categoryData = {
        name: formName,
        description: formDescription,
      };
      
      if (selectedCategory && selectedCategory.id) {
        // Update existing category
        const updated = await updateCategory(selectedCategory.id, categoryData);
        
        // Update in local state
        categories = categories.map(c => 
          c.id === selectedCategory?.id ? updated : c
        );
        
        selectedCategory = updated;
      } else {
        // Create new category
        const created = await createCategory(categoryData);
        
        // Add to local state
        categories = [...categories, created];
        selectedCategory = created;
      }
      
      // Exit edit mode
      editMode = false;
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to save category');
    } finally {
      isSaving = false;
    }
  }
  
  function cancelEdit() {
    editMode = false;
  }
</script>

<div class="container mx-auto p-4 space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Categories</h1>
    <button 
      onclick={addNewCategory}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md flex items-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      New Category
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
        onclick={loadCategories}
      >
        Retry
      </button>
    </div>
  {:else}
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Left side: Categories List -->
      <div class="w-full lg:w-2/3">
        {#if !hasCategories}
          <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-400 mb-4">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
            <h3 class="text-lg font-semibold mb-2">No Categories Found</h3>
            <p class="text-surface-400 mb-4">Create your first category to organize benchmark tasks</p>
            <button 
              onclick={addNewCategory}
              class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
            >
              Create First Category
            </button>
          </div>
        {:else}
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each categories as category}
              <div 
                class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedCategory?.id === category.id ? 'border-primary-500 ring-1 ring-primary-500' : ''}"
                onclick={() => selectCategory(category)}
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
                        selectCategory(category);
                        editSelectedCategory();
                      }}
                      class="p-1.5 hover:bg-surface-600 rounded-md"
                      aria-label="Edit category"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                      </svg>
                    </button>
                    <button 
                      onclick={(e) => {
                        e.stopPropagation();
                        handleDeleteCategory(category.id);
                      }}
                      class="p-1.5 hover:bg-surface-600 rounded-md text-red-400" 
                      aria-label="Delete category"
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
              </div>
            {/each}
          </div>
        {/if}
      </div>
      
      <!-- Right side: Category Details or Edit Form -->
      <div class="w-full lg:w-1/3">
        <div class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden">
          <div class="bg-surface-700 px-4 py-3">
            <h2 class="text-lg font-medium">
              {#if editMode}
                {selectedCategory ? 'Edit Category' : 'New Category'}
              {:else if selectedCategory}
                Category Details
              {:else}
                Select a Category
              {/if}
            </h2>
          </div>
          
          <div class="p-4">
            {#if editMode}
              <!-- Category Edit Form -->
              <form class="space-y-4">
                <div>
                  <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name*</label>
                  <input
                    id="name"
                    type="text"
                    bind:value={formName}
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
                    bind:value={formDescription}
                    class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
                    placeholder="Category description"
                  ></textarea>
                </div>
                
                <div class="flex space-x-3 pt-4">
                  <button
                    type="submit"
                    onclick={(e) => {
                      e.preventDefault();
                      saveCategory();
                    }}
                    disabled={isSaving}
                    class="px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1 flex items-center justify-center"
                  >
                    {#if isSaving}
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    {/if}
                    {selectedCategory ? 'Update' : 'Create'} Category
                  </button>
                  <button
                    type="button"
                    onclick={cancelEdit}
                    class="px-4 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            {:else if selectedCategory}
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
                  <button 
                    onclick={editSelectedCategory} 
                    class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">
                    Edit
                  </button>
                  <button 
                    onclick={() => {
                      if (selectedCategory) handleDeleteCategory(selectedCategory.id);
                    }}
                    class="px-3 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1">
                    Delete
                  </button>
                </div>
              </div>
            {:else}
              <!-- No category selected -->
              <div class="text-center py-8">
                <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-500 mb-4">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                  <line x1="10" y1="9" x2="8" y2="9"></line>
                </svg>
                <p class="text-surface-400 mb-4">Select a category to view details<br>or create a new one</p>
                <button 
                  onclick={addNewCategory}
                  class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
                >
                  Create Category
                </button>
              </div>
            {/if}
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>