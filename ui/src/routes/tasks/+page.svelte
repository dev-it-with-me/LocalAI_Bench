<script lang="ts">
  import { getTasks, getCategories, getTemplates, createTask, updateTask, deleteTask as apiDeleteTask } from '$lib/services/api';
  
  // Task related types
  type Category = {
    id: string;
    name: string;
  };
  
  type Template = {
    id: string;
    name: string;
    description: string;
    input_schema: Record<string, any>;
    output_schema: Record<string, any>;
  };
  
  type Task = {
    id: string;
    name: string;
    description: string;
    category_id: string;
    template_id: string;
    input_data: Record<string, any>;
    expected_output: Record<string, any>;
    complexity: number;
    created_at: string;
    updated_at: string;
    accuracy_weight: number;
    latency_weight: number;
    throughput_weight: number;
    cost_weight: number;
  };
  
  // State management using Svelte 5 runes
  let tasks = $state<Task[]>([]);
  let categories = $state<Category[]>([]);
  let templates = $state<Template[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedTask = $state<Task | null>(null);
  let selectedTemplate = $state<Template | null>(null);
  
  // Filter state
  let filterCategory = $state<string>('all');
  
  // Form state
  let editMode = $state(false);
  let formName = $state('');
  let formDescription = $state('');
  let formCategoryId = $state('');
  let formTemplateId = $state('');
  let formInputData = $state<Record<string, any>>({});
  let formExpectedOutput = $state<Record<string, any>>({});
  let formComplexity = $state(1);
  let formAccuracyWeight = $state(1);
  let formLatencyWeight = $state(1);
  let formThroughputWeight = $state(1);
  let formCostWeight = $state(1);
  
  // Right panel state
  let configurationTitle = $state('Task Editor');
  let hasConfigContent = $state(false);
  let configContent = $state<any>(null);
  
  // Derived properties
  let hasTasks = $derived(tasks.length > 0);
  let filteredTasks = $derived(
    filterCategory === 'all' 
      ? tasks 
      : tasks.filter(task => task.category_id === filterCategory)
  );
  
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

  loadData();
  
  function selectTask(task: Task) {
    selectedTask = task;
    
    // Find the associated template
    selectedTemplate = templates.find(t => t.id === task.template_id) || null;
    
    configurationTitle = `Task: ${task.name}`;
    hasConfigContent = true;
    configContent = TaskDetails;
  }
  
  function addNewTask() {
    editMode = false;
    formName = '';
    formDescription = '';
    formCategoryId = categories.length > 0 ? categories[0].id : '';
    formTemplateId = '';
    formInputData = {};
    formExpectedOutput = {};
    formComplexity = 1;
    formAccuracyWeight = 1;
    formLatencyWeight = 1;
    formThroughputWeight = 1;
    formCostWeight = 1;
    selectedTemplate = null;
    
    configurationTitle = 'Add New Task';
    hasConfigContent = true;
    configContent = TaskForm;
  }
  
  function editTask(task: Task) {
    editMode = true;
    formName = task.name;
    formDescription = task.description;
    formCategoryId = task.category_id;
    formTemplateId = task.template_id;
    formInputData = { ...task.input_data };
    formExpectedOutput = { ...task.expected_output };
    formComplexity = task.complexity;
    formAccuracyWeight = task.accuracy_weight;
    formLatencyWeight = task.latency_weight;
    formThroughputWeight = task.throughput_weight;
    formCostWeight = task.cost_weight;
    
    // Set the selected template for schema validation
    selectedTemplate = templates.find(t => t.id === task.template_id) || null;
    
    configurationTitle = `Edit Task: ${task.name}`;
    hasConfigContent = true;
    configContent = TaskForm;
  }
  
  async function deleteTask(taskId: string) {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }
    
    try {
      await apiDeleteTask(taskId);
      
      // Remove from local state
      tasks = tasks.filter(t => t.id !== taskId);
      
      // Reset selection if deleted task was selected
      if (selectedTask?.id === taskId) {
        selectedTask = null;
        hasConfigContent = false;
      }
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to delete task');
    }
  }
  
  function handleTemplateChange(templateId: string) {
    formTemplateId = templateId;
    selectedTemplate = templates.find(t => t.id === templateId) || null;
    
    // Reset input/output data when template changes
    formInputData = {};
    formExpectedOutput = {};
  }
  
  async function saveTask() {
    // Basic validation
    if (!formName.trim()) {
      alert('Task name is required');
      return;
    }
    
    if (!formTemplateId) {
      alert('Please select a template');
      return;
    }
    
    try {
      if (editMode && selectedTask?.id) {  // Add null check here
        // Update existing task
        const updated = await updateTask(selectedTask.id, {
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
        
        // Update in local state
        tasks = tasks.map(t => t.id === selectedTask?.id ? updated : t);  // Add null check
        selectedTask = updated;
      } else {
        // Create new task
        const created = await createTask({
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
        
        // Add to local state
        tasks = [...tasks, created];
        selectedTask = created;
      }
      
      // Switch back to task details view
      configurationTitle = `Task: ${selectedTask?.name}`;
      configContent = TaskDetails;
    } catch (e) {
      alert(e instanceof Error ? e.message : 'Failed to save task');
    }
  }
  
  function getCategoryName(categoryId: string): string {
    return categories.find(c => c.id === categoryId)?.name || 'Unknown';
  }
  
  function getTemplateName(templateId: string): string {
    return templates.find(t => t.id === templateId)?.name || 'Unknown';
  }
  
  // Utility function to render JSON editor
  function renderJsonEditor(label: string, value: Record<string, any>, onChange: (value: Record<string, any>) => void, schema?: Record<string, any>) {
    const jsonString = JSON.stringify(value, null, 2);
    
    return `
      <div>
        <label class="block text-sm font-medium text-surface-200 mb-1">${label}</label>
        <textarea
          rows="8"
          oninput=${(e: Event) => {
            try {
              const newValue = JSON.parse((e.target as HTMLTextAreaElement).value);
              onChange(newValue);
            } catch (e) {
              // Invalid JSON, don't update the value
            }
          }}
          class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white font-mono text-sm focus:ring-primary-500 focus:border-primary-500"
        >${jsonString}</textarea>
        ${schema ? 
        `<div class="mt-2 px-3 py-2 bg-surface-800 rounded-md">
          <h4 class="text-xs font-medium text-surface-300 mb-1">Schema:</h4>
          <pre class="text-xs text-surface-300 overflow-x-auto">${JSON.stringify(schema, null, 2)}</pre>
        </div>` : ''}
      </div>
    `;
  }
  
  // Task details component for the right panel
  const TaskDetails = {
    render: () => {
      if (!selectedTask) return null;
      
      return `
        <div class="space-y-4">
          <div>
            <div class="flex items-center mb-2">
              <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium mr-2">
                ${getCategoryName(selectedTask.category_id)}
              </span>
              <span class="px-2 py-0.5 bg-primary-900/50 text-primary-200 rounded text-xs font-medium">
                ${getTemplateName(selectedTask.template_id)}
              </span>
            </div>
            <h3 class="text-lg font-semibold mb-2">${selectedTask.name}</h3>
            <p class="text-surface-200">${selectedTask.description || 'No description'}</p>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <h4 class="font-medium mb-2">Task Input</h4>
            <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">${JSON.stringify(selectedTask.input_data, null, 2)}</pre>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <h4 class="font-medium mb-2">Expected Output</h4>
            <pre class="bg-surface-800 p-3 rounded-md text-sm overflow-x-auto">${JSON.stringify(selectedTask.expected_output, null, 2)}</pre>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <div class="flex justify-between items-center mb-2">
              <span class="text-surface-300">Complexity</span>
              <span class="font-medium">${selectedTask.complexity}</span>
            </div>
            <div class="h-2 bg-surface-700 rounded-full overflow-hidden">
              <div class="bg-primary-500 h-full" style="width: ${Math.min(selectedTask.complexity * 25, 100)}%"></div>
            </div>
          </div>
          
          <div class="pt-2 border-t border-surface-700">
            <h4 class="font-medium mb-2">Scoring Weights</h4>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="text-sm text-surface-300">Accuracy</span>
                <div class="flex items-center">
                  <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                    <div class="bg-green-500 h-full" style="width: ${Math.min(selectedTask.accuracy_weight * 25, 100)}%"></div>
                  </div>
                  <span class="ml-2 text-sm min-w-[2rem] text-center">${selectedTask.accuracy_weight}</span>
                </div>
              </div>
              <div>
                <span class="text-sm text-surface-300">Latency</span>
                <div class="flex items-center">
                  <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                    <div class="bg-blue-500 h-full" style="width: ${Math.min(selectedTask.latency_weight * 25, 100)}%"></div>
                  </div>
                  <span class="ml-2 text-sm min-w-[2rem] text-center">${selectedTask.latency_weight}</span>
                </div>
              </div>
              <div>
                <span class="text-sm text-surface-300">Throughput</span>
                <div class="flex items-center">
                  <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                    <div class="bg-yellow-500 h-full" style="width: ${Math.min(selectedTask.throughput_weight * 25, 100)}%"></div>
                  </div>
                  <span class="ml-2 text-sm min-w-[2rem] text-center">${selectedTask.throughput_weight}</span>
                </div>
              </div>
              <div>
                <span class="text-sm text-surface-300">Cost</span>
                <div class="flex items-center">
                  <div class="h-2 flex-1 bg-surface-700 rounded-full overflow-hidden">
                    <div class="bg-red-500 h-full" style="width: ${Math.min(selectedTask.cost_weight * 25, 100)}%"></div>
                  </div>
                  <span class="ml-2 text-sm min-w-[2rem] text-center">${selectedTask.cost_weight}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="pt-4 border-t border-surface-700">
            <div class="flex justify-between text-sm text-surface-400">
              <span>Created: ${new Date(selectedTask.created_at).toLocaleDateString()}</span>
              <span>Updated: ${new Date(selectedTask.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
          
          <div class="flex space-x-2 pt-4">
            <button onclick=${() => editTask(selectedTask!)} class="px-3 py-1 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1">Edit</button>
            <button onclick=${() => deleteTask(selectedTask!.id)} class="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600 flex-1">Delete</button>
          </div>
        </div>
      `;
    }
  };
  
  // Task form component for the right panel
  const TaskForm = {
    render: () => {
      return `
        <form class="space-y-4">
          <div>
            <label for="name" class="block text-sm font-medium text-surface-200 mb-1">Name</label>
            <input
              id="name"
              type="text"
              value="${formName}"
              oninput=${(e: Event) => {
                formName = (e.target as HTMLInputElement).value;
              }}
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
              oninput=${(e: Event) => {
                formDescription = (e.target as HTMLTextAreaElement).value;
              }}
              class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
              placeholder="Task description"
            >${formDescription}</textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="category" class="block text-sm font-medium text-surface-200 mb-1">Category</label>
              <select
                id="category"
                onchange=${(e: Event) => {
                  formCategoryId = (e.target as HTMLSelectElement).value;
                }}
                class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
                required
              >
                <option value="" disabled ${!formCategoryId ? 'selected' : ''}>Select category</option>
                ${categories.map(category => 
                  `<option value="${category.id}" ${formCategoryId === category.id ? 'selected' : ''}>${category.name}</option>`
                ).join('')}
              </select>
            </div>
            
            <div>
              <label for="template" class="block text-sm font-medium text-surface-200 mb-1">Template</label>
              <select
                id="template"
                onchange=${(e: Event) => {
                  handleTemplateChange((e.target as HTMLSelectElement).value);
                }}
                class="w-full px-3 py-2 bg-surface-700 border border-surface-600 rounded-md text-white focus:ring-primary-500 focus:border-primary-500"
                required
              >
                <option value="" disabled ${!formTemplateId ? 'selected' : ''}>Select template</option>
                ${templates.map(template => 
                  `<option value="${template.id}" ${formTemplateId === template.id ? 'selected' : ''}>${template.name}</option>`
                ).join('')}
              </select>
            </div>
          </div>
          
          ${selectedTemplate ? 
            `<div class="space-y-4 pt-2 border-t border-surface-700">
              ${renderJsonEditor(
                'Input Data', 
                formInputData, 
                (value) => { formInputData = value; }, 
                selectedTemplate.input_schema
              )}
              
              ${renderJsonEditor(
                'Expected Output', 
                formExpectedOutput, 
                (value) => { formExpectedOutput = value; }, 
                selectedTemplate.output_schema
              )}
            </div>` 
            : 
            `<div class="text-sm text-surface-400 italic">Select a template to configure input and output data</div>`
          }
          
          <div>
            <label for="complexity" class="block text-sm font-medium text-surface-200 mb-1">Complexity (0.5 - 4.0)</label>
            <div class="flex items-center">
              <input
                type="range"
                id="complexity"
                min="0.5"
                max="4"
                step="0.1"
                value="${formComplexity}"
                oninput=${(e: Event) => {
                  formComplexity = parseFloat((e.target as HTMLInputElement).value);
                }}
                class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
              />
              <span class="ml-2 text-sm min-w-[2.5rem] text-center">${formComplexity}</span>
            </div>
          </div>
          
          <div class="space-y-4 pt-2 border-t border-surface-700">
            <h4 class="font-medium">Scoring Weights (0.5 - 4.0)</h4>
            
            <div>
              <label class="block text-sm font-medium text-surface-200 mb-1">Accuracy Weight</label>
              <div class="flex items-center">
                <input
                  type="range"
                  min="0.5"
                  max="4"
                  step="0.1"
                  value="${formAccuracyWeight}"
                  oninput=${(e: Event) => {
                    formAccuracyWeight = parseFloat((e.target as HTMLInputElement).value);
                  }}
                  class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
                />
                <span class="ml-2 text-sm min-w-[2.5rem] text-center">${formAccuracyWeight}</span>
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
                  value="${formLatencyWeight}"
                  oninput=${(e: Event) => {
                    formLatencyWeight = parseFloat((e.target as HTMLInputElement).value);
                  }}
                  class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
                />
                <span class="ml-2 text-sm min-w-[2.5rem] text-center">${formLatencyWeight}</span>
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
                  value="${formThroughputWeight}"
                  oninput=${(e: Event) => {
                    formThroughputWeight = parseFloat((e.target as HTMLInputElement).value);
                  }}
                  class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
                />
                <span class="ml-2 text-sm min-w-[2.5rem] text-center">${formThroughputWeight}</span>
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
                  value="${formCostWeight}"
                  oninput=${(e: Event) => {
                    formCostWeight = parseFloat((e.target as HTMLInputElement).value);
                  }}
                  class="w-full h-2 bg-surface-600 rounded-lg appearance-none cursor-pointer"
                />
                <span class="ml-2 text-sm min-w-[2.5rem] text-center">${formCostWeight}</span>
              </div>
            </div>
          </div>
          
          <div class="flex space-x-2 pt-4">
            <button
              type="submit"
              onclick=${(e: Event) => {
                e.preventDefault();
                saveTask();
              }}
              class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1"
            >
              ${editMode ? 'Update' : 'Create'} Task
            </button>
            <button
              type="button"
              onclick=${() => {
                if (selectedTask) {
                  configContent = TaskDetails;
                  configurationTitle = `Task: ${selectedTask.name}`;
                } else {
                  hasConfigContent = false;
                }
              }}
              class="px-3 py-2 bg-surface-600 text-white rounded-md hover:bg-surface-500 flex-1"
            >
              Cancel
            </button>
          </div>
        </form>
      `;
    }
  };
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
          isLoading = true;
          // Retry loading
          setTimeout(() => {
            isLoading = false;
          }, 1000);
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
    <div class="space-y-3">
      {#each filteredTasks as task}
        <div 
          class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedTask?.id === task.id ? 'border-primary-500 ring-1 ring-primary-500' : ''}"
          onclick={() => selectTask(task)}
        >
          <div class="p-4">
            <div class="flex items-center mb-2">
              <span class="px-2 py-0.5 bg-surface-700 rounded text-xs font-medium mr-2">
                {getCategoryName(task.category_id)}
              </span>
              <span class="px-2 py-0.5 bg-primary-900/50 text-primary-200 rounded text-xs font-medium">
                {getTemplateName(task.template_id)}
              </span>
            </div>
            <h3 class="text-lg font-semibold mb-1">{task.name}</h3>
            <p class="text-surface-300 text-sm line-clamp-2">{task.description || 'No description'}</p>
          </div>
          <div class="bg-surface-700/50 px-4 py-2 flex justify-between items-center">
            <div class="flex items-center">
              <span class="text-sm text-surface-300 mr-1">Complexity:</span>
              <span class="text-sm font-medium">{task.complexity}</span>
            </div>
            <div class="flex space-x-1">
              <button 
                onclick={(e) => {
                  e.stopPropagation();
                  editTask(task);
                }}
                class="p-1.5 hover:bg-surface-600 rounded-md"
                aria-label="Edit task"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button 
                onclick={(e) => {
                  e.stopPropagation();
                  deleteTask(task.id);
                }}
                class="p-1.5 hover:bg-surface-600 rounded-md text-red-400" 
                aria-label="Delete task"
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