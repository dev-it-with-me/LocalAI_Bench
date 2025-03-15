<script lang="ts">
  // No props required for this component
</script>

<div class="bg-surface-800 rounded-lg p-6">
  <h2 class="mb-4 text-xl font-semibold">Quick Actions</h2>
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
    <a
      href="/models"
      class="bg-surface-700 hover:bg-surface-600 flex flex-col items-center rounded-lg p-4 transition"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-primary-400 mb-2"
      >
        <path
          d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
        ></path>
        <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
        <line x1="12" y1="22.08" x2="12" y2="12"></line>
      </svg>
      <span class="text-sm font-medium">Manage Models</span>
    </a>
    <a
      href="/tasks"
      class="bg-surface-700 hover:bg-surface-600 flex flex-col items-center rounded-lg p-4 transition"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-secondary-400 mb-2"
      >
        <polyline points="9 11 12 14 22 4"></polyline>
        <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
      </svg>
      <span class="text-sm font-medium">Create Task</span>
    </a>
    <a
      href="/categories"
      class="bg-surface-700 hover:bg-surface-600 flex flex-col items-center rounded-lg p-4 transition"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-tertiary-400 mb-2"
      >
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
        ></path>
      </svg>
      <span class="text-sm font-medium">Browse Categories</span>
    </a>
    <a
      href="/results"
      class="bg-surface-700 hover:bg-surface-600 flex flex-col items-center rounded-lg p-4 transition"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="24"
        height="24"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="text-success-400 mb-2"
      >
        <line x1="18" y1="20" x2="18" y2="10"></line>
        <line x1="12" y1="20" x2="12" y2="4"></line>
        <line x1="6" y1="20" x2="6" y2="14"></line>
      </svg>
      <span class="text-sm font-medium">View Results</span>
    </a>
  </div>
</div>