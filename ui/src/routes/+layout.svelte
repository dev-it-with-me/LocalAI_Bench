<script lang="ts">
	import '$lib/../app.postcss';
	import LeftSidebar from '$lib/components/LeftSidebar.svelte';
	import RightPanel from '$lib/components/RightPanel.svelte';
	import StatusBar from '$lib/components/StatusBar.svelte';
	import { AppShell } from '@skeletonlabs/skeleton';

	let { children } = $props();

	// App state
	let leftSidebarExpanded = $state(true);
	let activeModel = $state(''); // Define the activeModel state
	let currentOperation = $state('');
	let configurationTitle = $state('Configuration');
	let hasConfigContent = $state(false);
	let configContent = $state<any>(null);
</script>

<AppShell slotSidebarLeft={leftSidebarExpanded ? 'w-64' : 'w-16'} slotHeader="bg-surface-100-800-token">
	<div class="bg-surface-900 flex h-full flex-col text-white">
		<main class="flex flex-1 overflow-hidden">
			<!-- Left Sidebar Navigation -->
			<LeftSidebar expanded={leftSidebarExpanded} />

			<!-- Main Content Area -->
			<div class="flex-1 overflow-y-auto p-6"> 
				{@render children()}
			</div>

			<!-- Right Configuration Panel -->
			<RightPanel title={configurationTitle} hasContent={hasConfigContent}>
				{#if configContent}
					{configContent}
				{/if}
			</RightPanel>
		</main>

		<!-- Status Bar -->
		<StatusBar {activeModel} {currentOperation} />
	</div>
</AppShell>

<style>
	:global(html, body) {
		height: 100%;
		overflow: hidden;
		margin: 0;
		padding: 0;
	}

	:global(#svelte) {
		height: 100%;
	}
</style>
