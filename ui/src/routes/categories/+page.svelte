<script lang="ts">
  import { getCategories, createCategory, updateCategory, deleteCategory } from '$lib/services/api';
  import CategoryList from '$lib/components/categories/CategoryList.svelte';
  import CategoryDetails from '$lib/components/categories/CategoryDetails.svelte';
  import CategoryForm from '$lib/components/categories/CategoryForm.svelte';
  import { getContext } from 'svelte';
  import { onMount } from 'svelte';
  import type { CategoryModel, CategoryCreateRequest, CategoryUpdateRequest } from '$lib/services/type';

  // Access layout store to update right panel content
  const layout: any = getContext('layout');

  // State management using Svelte 5 runes
  let categories = $state<CategoryModel[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedCategory = $state<CategoryModel | null>(null);

  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let isSaving = $state(false);

  // Update the right panel content whenever selection or edit mode changes
  $effect(() => {
    updateRightPanel();
  });

  function updateRightPanel() {
    if (editMode) {
      // Set form in right panel
      layout.configurationTitle = selectedCategory ? 'Edit Category' : 'New Category';
      layout.hasConfigContent = true;
      
      // Directly set component and props using a function
      layout.configContent = () => ({
        component: CategoryForm,
        props: {
          selectedCategory,
          formName,
          formDescription,
          isSaving,
          onSaveCategory: saveCategory,
          onCancelEdit: cancelEdit
        }
      });
    } else if (selectedCategory) {
      // Set details in right panel
      layout.configurationTitle = 'Category Details';
      layout.hasConfigContent = true;
      
      // Directly set component and props using a function
      layout.configContent = () => ({
        component: CategoryDetails,
        props: {
          selectedCategory,
          onEditCategory: editSelectedCategory,
          onDeleteCategory: handleDeleteCategory,
          onAddNewCategory: addNewCategory
        }
      });
    } else {
      // Clear right panel
      layout.configurationTitle = 'Category';
      layout.hasConfigContent = false;
      layout.configContent = null;
    }
  }

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

  // Load categories on component mount (client-side only)
  onMount(() => {
    loadCategories();
  });

  function selectCategory(category: CategoryModel) {
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

  async function saveCategory(categoryData: CategoryCreateRequest | CategoryUpdateRequest) {
    try {
      isSaving = true;

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
        const created = await createCategory(categoryData as CategoryCreateRequest);

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

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Categories</h1>
    <button
      onclick={addNewCategory}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md flex items-center"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="16"
        height="16"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="mr-2"
      >
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
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
      <button class="mt-2 px-4 py-1 bg-red-800 hover:bg-red-700 rounded-md" onclick={loadCategories}>
        Retry
      </button>
    </div>
  {:else}
    <div class="w-full">
      <CategoryList
        categories={categories}
        selectedCategory={selectedCategory}
        onSelectCategory={selectCategory}
        onEditCategory={editSelectedCategory}
        onDeleteCategory={handleDeleteCategory}
        onAddNewCategory={addNewCategory}
      />
    </div>
  {/if}
</div>