<script lang="ts">
  import { getBenchmarks, getModels, getCategories, getTasks } from '$lib/services/api';
  
  // Types
  type BenchmarkStatus = 'idle' | 'running' | 'completed' | 'failed';
  type BenchmarkRun = {
    id: string;
    name: string;
    description: string;
    status: BenchmarkStatus;
    progress: number;
    models: string[];
    categories: string[];
    tasks: string[];
    results: BenchmarkResult[];
    created_at: string;
    updated_at: string;
    error?: string;
  };
  type BenchmarkResult = {
    model_id: string;
    task_id: string;
    execution_time: number;
    memory_usage: number;
    output: string;
    score: number;
    error?: string;
  };
  
  // State management using Svelte 5 runes
  let benchmarks = $state<BenchmarkRun[]>([]);
  let models = $state<{ id: string; name: string }[]>([]);
  let categories = $state<{ id: string; name: string }[]>([]);
  let tasks = $state<{ id: string; name: string; category_id: string }[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);
  let selectedBenchmark = $state<BenchmarkRun | null>(null);
  
  // Form state
  let formName = $state('');
  let formDescription = $state('');
  let selectedModels = $state<Set<string>>(new Set());
  let selectedCategories = $state<Set<string>>(new Set());
  let selectedTasks = $state<Set<string>>(new Set());
  
  // Right panel state
  let configurationTitle = $state('Benchmark Details');
  let hasConfigContent = $state(false);
  let configContent = $state<any>(null);
  
  // Derived properties
  let hasBenchmarks = $derived(benchmarks.length > 0);
  let filteredTasks = $derived(() => {
    if (selectedCategories.size === 0) return tasks;
    return tasks.filter(task => selectedCategories.has(task.category_id));
  });
  
  async function loadData() {
    try {
      const [benchmarksData, modelsData, categoriesData, tasksData] = await Promise.all([
        getBenchmarks(),
        getModels(),
        getCategories(),
        getTasks()
      ]);
      
      benchmarks = benchmarksData;
      models = modelsData;
      categories = categoriesData;
      tasks = tasksData;
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load data';
    } finally {
      isLoading = false;
    }
  }

  loadData();
  
  function selectBenchmark(benchmark: BenchmarkRun) {
    selectedBenchmark = benchmark;
    configurationTitle = `Benchmark: ${benchmark.name}`;
    hasConfigContent = true;
    configContent = BenchmarkDetails;
  }
  
  function startNewBenchmark() {
    formName = '';
    formDescription = '';
    selectedModels.clear();
    selectedCategories.clear();
    selectedTasks.clear();
    configurationTitle = 'New Benchmark';
    hasConfigContent = true;
    configContent = BenchmarkForm;
  }
  
  function deleteBenchmark(benchmarkId: string) {
    if (confirm('Are you sure you want to delete this benchmark run?')) {
      // In a real app, delete via API
      benchmarks = benchmarks.filter(b => b.id !== benchmarkId);
      
      if (selectedBenchmark?.id === benchmarkId) {
        selectedBenchmark = null;
        hasConfigContent = false;
      }
    }
  }
  
  async function runBenchmark() {
    if (!formName.trim()) {
      alert('Benchmark name is required');
      return;
    }
    
    if (selectedModels.size === 0) {
      alert('Please select at least one model');
      return;
    }
    
    if (selectedTasks.size === 0) {
      alert('Please select at least one task');
      return;
    }
    
    // Create new benchmark run
    const newBenchmark: BenchmarkRun = {
      id: crypto.randomUUID(),
      name: formName,
      description: formDescription,
      status: 'running',
      progress: 0,
      models: Array.from(selectedModels),
      categories: Array.from(selectedCategories),
      tasks: Array.from(selectedTasks),
      results: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    benchmarks = [newBenchmark, ...benchmarks];
    selectedBenchmark = newBenchmark;
    
    // In a real app, start the benchmark via API
    // For demo, simulate progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      if (progress <= 100) {
        benchmarks = benchmarks.map(b =>
          b.id === newBenchmark.id
            ? { ...b, progress }
            : b
        );
        
        if (progress === 100) {
          clearInterval(interval);
          // Simulate results
          benchmarks = benchmarks.map(b =>
            b.id === newBenchmark.id
              ? {
                  ...b,
                  status: 'completed',
                  results: Array.from(selectedModels).flatMap(modelId =>
                    Array.from(selectedTasks).map(taskId => ({
                      model_id: modelId,
                      task_id: taskId,
                      execution_time: Math.random() * 5,
                      memory_usage: Math.random() * 4096,
                      output: 'Sample output',
                      score: Math.random()
                    }))
                  )
                }
              : b
          );
        }
      }
    }, 500);
    
    // Switch to benchmark details view
    configurationTitle = `Benchmark: ${newBenchmark.name}`;
    configContent = BenchmarkDetails;
  }
  
  function getModelName(modelId: string): string {
    return models.find(m => m.id === modelId)?.name || 'Unknown Model';
  }
  
  function getCategoryName(categoryId: string): string {
    return categories.find(c => c.id === categoryId)?.name || 'Unknown Category';
  }
  
  function getTaskName(taskId: string): string {
    return tasks.find(t => t.id === taskId)?.name || 'Unknown Task';
  }
  
  function formatNumber(num: number): string {
    return num.toFixed(2);
  }
  
  // Benchmark details component
  const BenchmarkDetails = {
    render: () => {
      if (!selectedBenchmark) return null;
      
      const isRunning = selectedBenchmark.status === 'running';
      const hasResults = selectedBenchmark.results.length > 0;
      
      // Calculate aggregate scores
      const modelScores = hasResults
        ? Object.fromEntries(
            Array.from(new Set(selectedBenchmark.results.map(r => r.model_id)))
              .map(modelId => {
                const modelResults = selectedBenchmark.results.filter(r => r.model_id === modelId);
                const avgScore = modelResults.reduce((sum, r) => sum + r.score, 0) / modelResults.length;
                return [modelId, avgScore];
              })
          )
        : {};
      
      return `
        <div class="space-y-6">
          <div>
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-0.5 rounded text-xs font-medium
                ${selectedBenchmark.status === 'completed' ? 'bg-green-900/50 text-green-200' :
                  selectedBenchmark.status === 'running' ? 'bg-blue-900/50 text-blue-200' :
                  selectedBenchmark.status === 'failed' ? 'bg-red-900/50 text-red-200' :
                  'bg-surface-700 text-surface-200'}"
              >
                ${selectedBenchmark.status.toUpperCase()}
              </span>
              <button 
                onclick=${() => deleteBenchmark(selectedBenchmark!.id)}
                class="text-red-400 hover:text-red-300"
                aria-label="Delete benchmark"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
            <h3 class="text-lg font-semibold mb-2">${selectedBenchmark.name}</h3>
            <p class="text-surface-200 mb-4">${selectedBenchmark.description || 'No description'}</p>
          </div>
          
          ${isRunning ? `
            <div class="space-y-2">
              <div class="flex justify-between text-sm">
                <span>Progress</span>
                <span>${selectedBenchmark.progress}%</span>
              </div>
              <div class="h-2 bg-surface-700 rounded-full overflow-hidden">
                <div class="bg-primary-500 h-full transition-all" style="width: ${selectedBenchmark.progress}%"></div>
              </div>
            </div>
          ` : ''}
          
          ${hasResults ? `
            <div class="space-y-6">
              <!-- Model Comparison -->
              <div>
                <h4 class="font-medium mb-3">Model Performance</h4>
                <div class="grid gap-4">
                  ${Object.entries(modelScores)
                    .sort(([, a], [, b]) => b - a)
                    .map(([modelId, score]) => `
                      <div class="bg-surface-800 p-4 rounded-md">
                        <div class="flex justify-between items-center mb-2">
                          <span class="font-medium">${getModelName(modelId)}</span>
                          <span class="text-sm">${formatNumber(score * 100)}%</span>
                        </div>
                        <div class="h-2 bg-surface-700 rounded-full overflow-hidden">
                          <div class="bg-primary-500 h-full" style="width: ${score * 100}%"></div>
                        </div>
                      </div>
                    `).join('')}
                </div>
              </div>
              
              <!-- Detailed Results -->
              <div>
                <h4 class="font-medium mb-3">Task Results</h4>
                <div class="space-y-4">
                  ${selectedBenchmark.tasks.map(taskId => `
                    <div class="bg-surface-800 rounded-md overflow-hidden">
                      <div class="p-4">
                        <h5 class="font-medium mb-2">${getTaskName(taskId)}</h5>
                        <div class="grid gap-4">
                          ${selectedBenchmark.results
                            .filter(r => r.task_id === taskId)
                            .sort((a, b) => b.score - a.score)
                            .map(result => `
                              <div>
                                <div class="flex justify-between items-center mb-1">
                                  <span class="text-sm">${getModelName(result.model_id)}</span>
                                  <span class="text-sm">${formatNumber(result.score * 100)}%</span>
                                </div>
                                <div class="text-xs text-surface-300 flex justify-between">
                                  <span>${formatNumber(result.execution_time)}s</span>
                                  <span>${formatNumber(result.memory_usage / 1024)}MB</span>
                                </div>
                                ${result.error ? `
                                  <div class="mt-2 text-sm text-red-400">${result.error}</div>
                                ` : `
                                  <pre class="mt-2 p-2 bg-surface-900 rounded text-xs overflow-x-auto">${result.output}</pre>
                                `}
                              </div>
                            `).join('')}
                        </div>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
          ` : ''}
          
          <div class="pt-4 border-t border-surface-700">
            <div class="flex justify-between text-sm text-surface-400">
              <span>Created: ${new Date(selectedBenchmark.created_at).toLocaleDateString()}</span>
              <span>Updated: ${new Date(selectedBenchmark.updated_at).toLocaleDateString()}</span>
            </div>
          </div>
        </div>
      `;
    }
  };
  
  // Benchmark form component
  const BenchmarkForm = {
    render: () => {
      return `
        <form class="space-y-6">
          <div class="space-y-4">
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
                placeholder="Benchmark name"
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
                placeholder="Benchmark description"
              >${formDescription}</textarea>
            </div>
          </div>
          
          <div class="space-y-4">
            <h4 class="font-medium">Select Models</h4>
            <div class="space-y-2">
              ${models.map(model => `
                <label class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    value="${model.id}"
                    ${selectedModels.has(model.id) ? 'checked' : ''}
                    onchange=${(e: Event) => {
                      const checked = (e.target as HTMLInputElement).checked;
                      if (checked) {
                        selectedModels.add(model.id);
                      } else {
                        selectedModels.delete(model.id);
                      }
                    }}
                    class="rounded border-surface-600 text-primary-500 focus:ring-primary-500 bg-surface-700"
                  />
                  <span>${model.name}</span>
                </label>
              `).join('')}
            </div>
          </div>
          
          <div class="space-y-4">
            <h4 class="font-medium">Filter by Categories</h4>
            <div class="space-y-2">
              ${categories.map(category => `
                <label class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    value="${category.id}"
                    ${selectedCategories.has(category.id) ? 'checked' : ''}
                    onchange=${(e: Event) => {
                      const checked = (e.target as HTMLInputElement).checked;
                      if (checked) {
                        selectedCategories.add(category.id);
                      } else {
                        selectedCategories.delete(category.id);
                      }
                    }}
                    class="rounded border-surface-600 text-primary-500 focus:ring-primary-500 bg-surface-700"
                  />
                  <span>${category.name}</span>
                </label>
              `).join('')}
            </div>
          </div>
          
          <div class="space-y-4">
            <h4 class="font-medium">Select Tasks</h4>
            <div class="space-y-2">
              ${filteredTasks.map(task => `
                <label class="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    value="${task.id}"
                    ${selectedTasks.has(task.id) ? 'checked' : ''}
                    onchange=${(e: Event) => {
                      const checked = (e.target as HTMLInputElement).checked;
                      if (checked) {
                        selectedTasks.add(task.id);
                      } else {
                        selectedTasks.delete(task.id);
                      }
                    }}
                    class="rounded border-surface-600 text-primary-500 focus:ring-primary-500 bg-surface-700"
                  />
                  <span>${task.name}</span>
                </label>
              `).join('')}
            </div>
          </div>
          
          <div class="flex space-x-2 pt-4">
            <button
              type="submit"
              onclick=${(e: Event) => {
                e.preventDefault();
                runBenchmark();
              }}
              class="px-3 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 flex-1"
            >
              Start Benchmark
            </button>
            <button
              type="button"
              onclick=${() => {
                hasConfigContent = false;
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
    <h1 class="text-2xl font-bold">Benchmarks</h1>
    <button 
      onclick={startNewBenchmark}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md flex items-center"
    >
      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mr-2">
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      New Benchmark
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
  {:else if !hasBenchmarks}
    <div class="bg-surface-800 border border-surface-700 rounded-md p-6 text-center">
      <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round" class="mx-auto text-surface-400 mb-4">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
      <h3 class="text-lg font-semibold mb-2">No Benchmarks Found</h3>
      <p class="text-surface-400 mb-4">Run your first benchmark to compare model performance</p>
      <button 
        onclick={startNewBenchmark}
        class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md"
      >
        Run First Benchmark
      </button>
    </div>
  {:else}
    <div class="space-y-4">
      {#each benchmarks as benchmark}
        <div 
          class="bg-surface-800 border border-surface-700 rounded-md overflow-hidden hover:border-primary-500 transition-colors cursor-pointer {selectedBenchmark?.id === benchmark.id ? 'border-primary-500 ring-1 ring-primary-500' : ''}"
          onclick={() => selectBenchmark(benchmark)}
        >
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <span class="px-2 py-0.5 rounded text-xs font-medium
                ${benchmark.status === 'completed' ? 'bg-green-900/50 text-green-200' :
                  benchmark.status === 'running' ? 'bg-blue-900/50 text-blue-200' :
                  benchmark.status === 'failed' ? 'bg-red-900/50 text-red-200' :
                  'bg-surface-700 text-surface-200'}"
              >
                ${benchmark.status.toUpperCase()}
              </span>
              <button 
                onclick={(e) => {
                  e.stopPropagation();
                  deleteBenchmark(benchmark.id);
                }}
                class="text-red-400 hover:text-red-300"
                aria-label="Delete benchmark"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
            
            <h3 class="text-lg font-semibold mb-1">{benchmark.name}</h3>
            <p class="text-surface-300 text-sm line-clamp-2">{benchmark.description || 'No description'}</p>
            
            {#if benchmark.status === 'running'}
              <div class="mt-4 space-y-2">
                <div class="flex justify-between text-sm">
                  <span>Progress</span>
                  <span>{benchmark.progress}%</span>
                </div>
                <div class="h-2 bg-surface-700 rounded-full overflow-hidden">
                  <div class="bg-primary-500 h-full transition-all" style="width: {benchmark.progress}%"></div>
                </div>
              </div>
            {:else if benchmark.status === 'completed'}
              <div class="mt-4 grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span class="text-surface-400">Models:</span>
                  <span class="font-medium">{benchmark.models.length}</span>
                </div>
                <div>
                  <span class="text-surface-400">Tasks:</span>
                  <span class="font-medium">{benchmark.tasks.length}</span>
                </div>
                <div>
                  <span class="text-surface-400">Results:</span>
                  <span class="font-medium">{benchmark.results.length}</span>
                </div>
              </div>
            {/if}
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>