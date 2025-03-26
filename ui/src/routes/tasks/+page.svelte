<script lang="ts">
  import { getTasks, getCategories, createTask, updateTask, deleteTask as apiDeleteTask } from '$lib/services/api';
  import TaskList from '$lib/components/tasks/TaskList.svelte';
  import TaskDetails from '$lib/components/tasks/TaskDetails.svelte';
  import TaskForm from '$lib/components/tasks/TaskForm.svelte';
  import { getContext } from 'svelte';
  import { onMount } from 'svelte';
  import type { TaskCreateRequest, TaskResponse, TaskUpdateRequest, Category } from '$lib/services/type';
  import { TaskStatusEnum } from '$lib/services/type';
  
  // Access layout store to update right panel content
  const layout: any = getContext('layout');

  // State management
  let tasks = $state<TaskResponse[]>([]);
  let categories = $state<Category[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedTask = $state<TaskResponse | null>(null);
  let isSaving = $state(false);
  
  // Filter state
  let filterCategory = $state<string>('all');
  let filterStatus = $state<TaskStatusEnum | 'all'>('all');
  let searchQuery = $state<string>('');
  
  // Status options for filtering
  const statusOptions = [
    { value: 'all', label: 'All Statuses' },
    { value: TaskStatusEnum.DRAFT, label: 'Draft' },
    { value: TaskStatusEnum.READY, label: 'Ready' },
    { value: TaskStatusEnum.ARCHIVED, label: 'Archived' }
  ];

  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let formCategoryId = $state('');
  let formInputData = $state<Record<string, any>>({});
  let formExpectedOutput = $state<string | null>(null);
  let formStatus = $state<TaskStatusEnum>(TaskStatusEnum.DRAFT);

  // Derived state
  let hasTasks = $derived(tasks.length > 0);
  
  let filteredTasks = $derived(() => {
    let filtered = [...tasks];
    
    // Apply category filter
    if (filterCategory !== 'all') {
      filtered = filtered.filter(task => task.category_id === filterCategory);
    }
    
    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(task => task.status === filterStatus);
    }
    
    // Apply search query filter
    if (searchQuery.trim() !== '') {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(task => 
        task.name.toLowerCase().includes(query) || 
        (task.description && task.description.toLowerCase().includes(query))
      );
    }
    
    return filtered;
  });

  // Update the right panel content whenever selection or edit mode changes
  $effect(() => {
    updateRightPanel();
  });

  function updateRightPanel() {
    if (editMode) {
      // Set form in right panel
      layout.configurationTitle = selectedTask ? `Edit Task: ${selectedTask.name}` : 'Add New Task';
      layout.hasConfigContent = true;
      
      // Directly set component and props using a function
      layout.configContent = () => ({
        component: TaskForm,
        props: {
          selectedTask,
          formName,
          formDescription,
          formCategoryId,
          formInputData,
          formExpectedOutput,
          formStatus,
          categories,
          isSaving,
          onSaveTask: handleSaveTask,
          onCancelEdit: cancelEdit
        }
      });
    } else if (selectedTask) {
      // Set details in right panel
      layout.configurationTitle = `Task: ${selectedTask.name}`;
      layout.hasConfigContent = true;
      
      // Directly set component and props using a function
      layout.configContent = () => ({
        component: TaskDetails,
        props: {
          selectedTask,
          categories,
          onEditTask: editTask,
          onDeleteTask: deleteTask
        }
      });
    } else {
      // Clear right panel
      layout.configurationTitle = 'Task Details';
      layout.hasConfigContent = false;
      layout.configContent = null;
    }
  }

  async function loadData() {
    try {
      const [tasksData, categoriesData] = await Promise.all([
        getTasks(),
        getCategories()
      ]);
      
      tasks = tasksData;
      categories = categoriesData;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to fetch data';
    } finally {
      isLoading = false;
    }
  }

  // Load initial data on component mount (client-side only)
  onMount(() => {
    loadData();
  });

  function resetForm() {
    formName = '';
    formDescription = '';
    formCategoryId = categories.length > 0 ? categories[0].id : '';
    formInputData = { user_instruction: '', system_prompt: null };
    formExpectedOutput = null;
    formStatus = TaskStatusEnum.DRAFT;
  }

  function selectTask(task: TaskResponse) {
    selectedTask = task;
    editMode = false;
  }

  function addNewTask() {
    editMode = true;
    selectedTask = null;
    resetForm();
  }
  
  function editTask(task: TaskResponse) {
    editMode = true;
    selectedTask = task;
    formName = task.name;
    formDescription = task.description;
    formCategoryId = task.category_id;
    formInputData = { ...task.input_data };
    formExpectedOutput = task.expected_output;
    formStatus = task.status;
  }
  
  async function deleteTask(taskId: string) {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }
    
    try {
      await apiDeleteTask(taskId);
      tasks = tasks.filter(t => t.id !== taskId);
      if (selectedTask?.id === taskId) {
        selectedTask = null;
        editMode = false;
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete task');
    }
  }

  function clearFilters() {
    filterCategory = 'all';
    filterStatus = 'all';
    searchQuery = '';
  }

  async function handleSaveTask(taskData: TaskCreateRequest | TaskUpdateRequest) {
    isSaving = true;
    try {
      if (selectedTask?.id) {
        const updated = await updateTask(selectedTask.id, taskData as TaskUpdateRequest);
        tasks = tasks.map(t => t.id === selectedTask?.id ? updated : t);
        selectedTask = updated;
      } else {
        const created = await createTask(taskData as TaskCreateRequest);
        tasks = [...tasks, created];
        selectedTask = created;
      }
      editMode = false;
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to save task');
    } finally {
      isSaving = false;
    }
  }

  function cancelEdit() {
    editMode = false;
    if (!selectedTask) {
      resetForm();
    }
  }

  // Computed property to track if no results after filtering
  let noFilterResults = $derived(tasks.length > 0 && filteredTasks().length === 0);
</script>

<div class="space-y-6">
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Tasks</h1>
    <button 
      onclick={addNewTask}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md flex items-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      New Task
    </button>
  </div>
  
  <!-- Search and Filter Bar -->
  <div class="flex flex-col gap-3">
    <div class="relative">
      <input
        type="text"
        bind:value={searchQuery}
        placeholder="Search tasks..."
        class="w-full px-3 py-2 pl-10 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
      />
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="absolute left-3 top-1/2 -translate-y-1/2 text-surface-400">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
    </div>
    
    <div class="flex gap-3 flex-col">
      <!-- Category filters -->
      <div class="flex flex-wrap gap-1">
        <button 
          class="px-3 py-1.5 rounded-md text-sm {filterCategory === 'all' ? 'bg-primary-500 text-white' : 'bg-surface-700 text-surface-200 hover:bg-surface-600'}"
          onclick={() => filterCategory = 'all'}
        >
          All Categories
        </button>
        {#each categories as category}
          <button 
            class="px-3 py-1.5 rounded-md text-sm {filterCategory === category.id ? 'bg-primary-500 text-white' : 'bg-surface-700 text-surface-200 hover:bg-surface-600'}"
            onclick={() => filterCategory = category.id}
          >
            {category.name}
          </button>
        {/each}
      </div>
      <!-- Status filters -->
      <div class="flex flex-wrap gap-1">
        {#each statusOptions as status}
          <button 
            class="px-3 py-1.5 rounded-md text-sm {filterStatus === status.value ? 'bg-primary-500 text-white' : 'bg-surface-700 text-surface-200 hover:bg-surface-600'}"
            onclick={() => filterStatus = status.value as any}
          >
            {status.label}
          </button>
        {/each}
      </div>
    </div>
    
    {#if searchQuery || filterCategory !== 'all' || filterStatus !== 'all'}
      <div class="flex justify-between items-center">
        <span class="text-sm text-surface-300">
          Found {filteredTasks.length} {filteredTasks.length === 1 ? 'task' : 'tasks'}
        </span>
        <button
          onclick={clearFilters}
          class="text-sm text-primary-400 hover:text-primary-300"
        >
          Clear filters
        </button>
      </div>
    {/if}
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
          loadData();
        }}
      >
        Retry
      </button>
    </div>
  {:else if !hasTasks}
    <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-400 mb-4">
        <polyline points="9 11 12 14 22 4"></polyline>
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
      </svg>
      <h3 class="text-lg font-semibold mb-2">No Tasks Found</h3>
      <p class="text-surface-400 mb-4">Create your first task to start benchmarking models</p>
      <button 
        onclick={addNewTask}
        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
      >
        Create First Task
      </button>
    </div>
  {:else if noFilterResults}
    <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-400 mb-4">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <h3 class="text-lg font-semibold mb-2">No Matching Tasks</h3>
      <p class="text-surface-400 mb-4">No tasks match your current filters</p>
      <button 
        onclick={clearFilters}
        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
      >
        Clear Filters
      </button>
    </div>
  {:else}
    <div class="w-full">
      <TaskList
        tasks={filteredTasks()}
        {selectedTask}
        {categories}
        onSelectTask={selectTask}
        onEditTask={editTask}
        onDeleteTask={deleteTask}
      />
    </div>
  {/if}
</div>