<script lang="ts">
	import { getModels } from '$lib/services/api';
	import ActiveModelsPanel from '$lib/components/ActiveModelsPanel.svelte';
	import RecentBenchmarksPanel from '$lib/components/RecentBenchmarksPanel.svelte';
	import QuickActionsPanel from '$lib/components/QuickActionsPanel.svelte';
	
	type ModelType = {
		name: string;
		type: string;
		status: string;
	};
	
	let activeModels = $state<ModelType[]>([]);
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
	
	let isLoading = $state(true);
	let error = $state('');
	async function loadModels() {
		try {
			activeModels = await getModels() as ModelType[];
		} catch (e) {
			if (e instanceof Error) {
				error = e.message;
			} else {
				error = String(e);
			}
		} finally {
			isLoading = false;
		}
	}
	loadModels();
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
			<ActiveModelsPanel {activeModels} {isLoading} {error} />
			<!-- Recent Benchmarks Panel -->
			<RecentBenchmarksPanel {recentBenchmarks} />
		</div>
		<!-- Quick Actions -->
		<QuickActionsPanel />
	{/if}
</div>
