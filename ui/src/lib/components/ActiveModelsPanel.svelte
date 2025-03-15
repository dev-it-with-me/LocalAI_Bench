<script lang="ts">
  // Using Svelte 5 props with runes
  let { activeModels, isLoading, error } = $props<{
    activeModels: Array<{
      name: string;
      type: string;
      status: string;
    }>;
    isLoading?: boolean;
    error?: string;
  }>();
</script>

<div class="bg-surface-800 rounded-lg p-6">
  <h2 class="mb-4 flex items-center text-xl font-semibold">
    <span class="text-primary-400 mr-2 flex h-6 w-6 items-center justify-center">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="20"
        height="20"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path
          d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
        ></path>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
        <line x1="12" y1="22.08" x2="12" y2="12"></line>
      </svg>
    </span>
    Active Models
  </h2>
  <div class="space-y-4">
    {#each activeModels as model}
      <div class="bg-surface-700 flex items-center justify-between rounded-md p-4">
        <div class="flex items-center">
          <div
            class="bg-primary-900 flex h-10 w-10 items-center justify-center rounded-full text-lg font-bold"
          >
            {model.name.charAt(0)}
          </div>
          <div class="ml-3">
            <h3 class="font-medium">{model.name}</h3>
            <p class="text-surface-300 text-sm">{model.type}</p>
          </div>
        </div>
        <div class="flex items-center">
          <span
            class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${model.status === 'active' ? 'bg-success-800 text-success-200' : 'bg-surface-600 text-surface-300'}`}
          >
            {model.status}
          </span>
        </div>
      </div>
    {/each}
    <button
      class="bg-primary-700 hover:bg-primary-600 mt-2 flex w-full items-center justify-center rounded-md py-2 transition"
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
        class="mr-1"
      >
        <line x1="12" y1="5" x2="12" y2="19"></line>
        <line x1="5" y1="12" x2="19" y2="12"></line>
      </svg>
      Add New Model
    </button>
  </div>
</div>