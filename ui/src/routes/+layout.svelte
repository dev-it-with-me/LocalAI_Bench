<script lang="ts">
	import '$lib/../app.postcss';
	import LeftSidebar from '$lib/components/LeftSidebar.svelte';
	import RightPanel from '$lib/components/RightPanel.svelte';
	import StatusBar from '$lib/components/StatusBar.svelte';
	import { AppShell } from '@skeletonlabs/skeleton';
	import { setContext } from 'svelte';

	let { children } = $props();

	// App state
	let leftSidebarExpanded = $state(true);
	let activeModel = $state(''); // Define the activeModel state
	let currentOperation = $state('');
	let configurationTitle = $state('Configuration');
	let hasConfigContent = $state(false);
	let configContent = $state<any>(null);
	
	// Create layout context for child components to access
	const layoutContext = {
		get configurationTitle() { return configurationTitle; },
		set configurationTitle(value: string) { configurationTitle = value; },
		
		get hasConfigContent() { return hasConfigContent; },
		set hasConfigContent(value: boolean) { hasConfigContent = value; },
		
		get configContent() { return configContent; },
		set configContent(value: any) { configContent = value; }
	};
	
	// Expose layout context to child components
	setContext('layout', layoutContext);
</script>

<AppShell slotSidebarLeft={leftSidebarExpanded ? 'w-64' : 'w-16'} slotHeader="bg-surface-100-800-token">
	<!-- Main Application Container with absolute positioning for StatusBar -->
	<div class="bg-surface-900 text-white flex flex-col h-full relative">
		<!-- Main Content Area -->
		<div class="absolute inset-0 bottom-8 flex overflow-hidden">
			<!-- Left Sidebar Navigation -->
			<LeftSidebar expanded={leftSidebarExpanded} />

			<!-- Main Content Area -->
			<div class="flex-1 overflow-y-auto p-6"> 
				{@render children()}
			</div>

			<!-- Right Configuration Panel -->
			<RightPanel title={configurationTitle} hasContent={hasConfigContent} children={configContent} />
		</div>

		<!-- Status Bar (fixed at bottom with absolute positioning) -->
		<div class="absolute bottom-0 left-0 right-0">
			<StatusBar {activeModel} {currentOperation} />
		</div>
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
