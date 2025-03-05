<script lang="ts">
	// Simple reactive state to simulate dashboard data
	let activeModels = $state([
		{ id: 'model1', name: 'Llama-2-7b', type: 'Ollama', status: 'active' },
		{ id: 'model2', name: 'Mistral-7B-Instruct', type: 'Hugging Face', status: 'active' },
		{ id: 'model3', name: 'GPT-J-6B', type: 'Hugging Face', status: 'inactive' }
	]);

	let recentBenchmarks = $state([
		{
			id: 'bench1',
			name: 'Coding UI Benchmark',
			date: '2023-10-15',
			status: 'completed',
			score: 87
		},
		{
			id: 'bench2',
			name: 'Document Understanding',
			date: '2023-10-14',
			status: 'completed',
			score: 92
		},
		{ id: 'bench3', name: 'Recruitment Process', date: '2023-10-13', status: 'failed', score: null }
	]);

	// Simulate loading state
	let isLoading = $state(true);

	// Simulate loading time
	setTimeout(() => {
		isLoading = false;
	}, 1000);
</script>

<svelte:head>
	<title>Dashboard | LocalAI Bench</title>
</svelte:head>

<div class="space-y-8">
	<header>
		<h1 class="mb-2 text-3xl font-bold">Dashboard</h1>
		<p class="text-surface-300">
			Welcome to LocalAI Bench. Your personal AI model benchmarking tool.
		</p>
	</header>

	{#if isLoading}
		<div class="grid animate-pulse grid-cols-1 gap-6 md:grid-cols-2">
			<div class="bg-surface-800 h-64 rounded-lg"></div>
			<div class="bg-surface-800 h-64 rounded-lg"></div>
		</div>
	{:else}
		<div class="grid grid-cols-1 gap-6 md:grid-cols-2">
			<!-- Active Models Panel -->
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

			<!-- Recent Benchmarks Panel -->
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
		</div>

		<!-- Quick Actions -->
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
	{/if}
</div>
