<script lang="ts">
  import { getTasks, getCategories, getTemplates, createTask, updateTask, deleteTask as apiDeleteTask } from '$lib/services/api';
  import TaskList from '$lib/components/tasks/TaskList.svelte';
  import TaskDetails from '$lib/components/tasks/TaskDetails.svelte';
  import TaskForm from '$lib/components/tasks/TaskForm.svelte';
  import { getContext } from 'svelte';
  import type { TaskCreateRequest, TaskResponse, TaskUpdateRequest, Category, Template } from '$lib/services/type';
  
  // Access layout store to update right panel content
  const layout: any = getContext('layout');

  // State management
  let tasks = $state<TaskResponse[]>([]);
  let categories = $state<Category[]>([]);
  let templates = $state<Template[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedTask = $state<TaskResponse | null>(null);
  let selectedTemplate = $state<Template | null>(null);
  let isSaving = $state(false);
  
  // Filter state
  let filterCategory = $state<string>('all');

  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let formCategoryId = $state('');
  let formTemplateId = $state('');
  let formInputData = $state<Record<string, any>>({});
  let formExpectedOutput = $state<string | null>(null);

  // Derived state
  let hasTasks = $derived(tasks.length > 0);
  let filteredTasks = $derived(
    filterCategory === 'all' 
      ? tasks 
      : tasks.filter(task => task.category_id === filterCategory)
  );

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
          formTemplateId,
          formInputData,
          formExpectedOutput,
          categories,
          templates,
          selectedTemplate,
          isSaving,
          onSaveTask: handleSaveTask,
          onCancelEdit: cancelEdit,
          onTemplateChange: handleTemplateChange
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
          selectedTemplate,
          categories,
          templates,
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
      const [tasksData, categoriesData, templatesData] = await Promise.all([
        getTasks(),
        getCategories(),
        getTemplates()
      ]);
      
      tasks = tasksData;
      categories = categoriesData;
      templates = templatesData;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to fetch data';
    } finally {
      isLoading = false;
    }
  }

  // Load initial data
  loadData();

  function resetForm() {
    formName = '';
    formDescription = '';
    formCategoryId = categories.length > 0 ? categories[0].id : '';
    formTemplateId = '';
    formInputData = {};
    formExpectedOutput = null;
    selectedTemplate = null;
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
    formTemplateId = task.template_id;
    formInputData = { ...task.input_data };
    formExpectedOutput = task.expected_output;
    selectedTemplate = templates.find(t => t.id === task.template_id) || null;
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

  function handleTemplateChange(templateId: string) {
    formTemplateId = templateId;
    selectedTemplate = templates.find(t => t.id === templateId) || null;
    formInputData = {};
    formExpectedOutput = null;
  }

  async function handleSaveTask(taskData: TaskCreateRequest | TaskUpdateRequest) {
    isSaving = true;
    try {
      if (selectedTask?.id) {
        const updated = await updateTask(selectedTask.id, taskData as TaskUpdateRequest);
        tasks = tasks.map(t => t.id === selectedTask.id ? updated : t);
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
  
  <!-- Filters -->
  <div class="flex space-x-2">
    <button 
      class="px-3 py-1.5 rounded-md text-sm {filterCategory === 'all' ? 'bg-primary-500 text-white' : 'bg-surface-700 text-surface-200 hover:bg-surface-600'}"
      onclick={() => filterCategory = 'all'}
    >
      All Tasks
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
  {:else if filteredTasks.length === 0}
    <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
      <p class="text-surface-400">No tasks found in this category</p>
    </div>
  {:else}
    <div class="w-full">
      <TaskList
        tasks={filteredTasks}
        {selectedTask}
        {categories}
        {templates}
        onSelectTask={selectTask}
        onEditTask={editTask}
        onDeleteTask={deleteTask}
      />
    </div>
  {/if}
</div>