<script lang="ts">
  // Using Svelte 5 props with runes
  let { recentBenchmarks } = $props<{
    recentBenchmarks: Array<{
      id: string;
      name: string;
      date: string;
      status: string;
      score: number | null;
    }>;
  }>();
</script>

<div class="bg-surface-800 rounded-lg p-6">
  <h2 class="mb-4 flex items-center text-xl font-semibold">
    <span class="text-secondary-400 mr-2 flex h-6 w-6 items-center justify-center">
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
        <line x1="18" y1="20" x2="18" y2="10"></line>
        <line x1="12" y1="20" x2="12" y2="4"></line>
        <line x1="6" y1="20" x2="6" y2="14"></line>
      </svg>
    </span>
    Recent Benchmarks
  </h2>
  <div class="space-y-4">
    {#each recentBenchmarks as benchmark}
      <div class="bg-surface-700 flex items-center justify-between rounded-md p-4">
        <div>
          <h3 class="font-medium">{benchmark.name}</h3>
          <p class="text-surface-300 text-sm">{benchmark.date}</p>
        </div>
        <div class="flex items-center space-x-2">
          <span
            class={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium
              ${
              benchmark.status === 'completed'
                ? 'bg-success-800 text-success-200'
                : benchmark.status === 'failed'
                  ? 'bg-error-900 text-error-200'
                  : 'bg-warning-900 text-warning-200'
            }`}
          >
            {benchmark.status}
          </span>
          {#if benchmark.score !== null}
            <span class="text-lg font-bold">{benchmark.score}</span>
          {/if}
        </div>
      </div>
    {/each}
    <button
      class="bg-secondary-700 hover:bg-secondary-600 mt-2 flex w-full items-center justify-center rounded-md py-2 transition"
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
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon>
      </svg>
      Run New Benchmark
    </button>
  </div>
</div>