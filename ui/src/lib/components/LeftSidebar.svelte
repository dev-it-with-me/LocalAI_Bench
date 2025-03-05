<script lang="ts">
	// Reactive state using Svelte 5 runes
	let isCollapsed = $state(false);

	// Navigation items
	const navItems = [
		{ title: 'Dashboard', icon: 'grid', path: '/' },
		{ title: 'Categories', icon: 'folder', path: '/categories' },
		{ title: 'Tasks', icon: 'check-square', path: '/tasks' },
		{ title: 'Models', icon: 'box', path: '/models' },
		{ title: 'Templates', icon: 'file-text', path: '/templates' },
		{ title: 'Results', icon: 'bar-chart', path: '/results' },
		{ title: 'Settings', icon: 'settings', path: '/settings' }
	];

	// Toggle sidebar collapse state
	function toggleSidebar(): void {
		isCollapsed = !isCollapsed;
	}
</script>

<aside
	class="bg-surface-800 border-surface-700 flex h-full flex-col border-r transition-all duration-300 {isCollapsed
		? 'w-16'
		: 'w-64'}"
>
	<!-- Header -->
	<div class="border-surface-700 flex items-center justify-between border-b p-4">
		{#if !isCollapsed}
			<h2 class="text-lg font-semibold text-white">LocalAI Bench</h2>
		{/if}
		<button
			onclick={toggleSidebar}
			class="hover:bg-surface-700 rounded-md p-1.5 text-white"
			aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
		>
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
				{#if isCollapsed}
					<polyline points="15 18 9 12 15 6"></polyline>
				{:else}
					<polyline points="9 18 15 12 9 6"></polyline>
				{/if}
			</svg>
		</button>
	</div>

	<!-- Navigation -->
	<nav class="flex-1 overflow-y-auto py-4">
		<ul class="space-y-2 px-2">
			{#each navItems as item}
				<li>
					<a
						href={item.path}
						class="hover:bg-surface-700 group flex items-center rounded-md p-3 text-white transition-colors"
						aria-label={item.title}
					>
						<span class="flex h-6 w-6 flex-shrink-0 items-center justify-center">
							<!-- Icon placeholder - would use an icon library in a full implementation -->
							<svg
								xmlns="http://www.w3.org/2000/svg"
								width="18"
								height="18"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
								stroke-linecap="round"
								stroke-linejoin="round"
							>
								{#if item.icon === 'grid'}
									<!-- Dashboard icon -->
									<rect x="3" y="3" width="7" height="7"></rect>
									<rect x="14" y="3" width="7" height="7"></rect>
									<rect x="3" y="14" width="7" height="7"></rect>
									<rect x="14" y="14" width="7" height="7"></rect>
								{:else if item.icon === 'folder'}
									<!-- Folder icon -->
									<path
										d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"
									></path>
								{:else if item.icon === 'check-square'}
									<!-- Task icon -->
									<polyline points="9 11 12 14 22 4"></polyline>
									<path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path>
								{:else if item.icon === 'box'}
									<!-- Models icon -->
									<path
										d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"
									></path>
									<polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
									<line x1="12" y1="22.08" x2="12" y2="12"></line>
								{:else if item.icon === 'file-text'}
									<!-- Templates icon -->
									<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
									<polyline points="14 2 14 8 20 8"></polyline>
									<line x1="16" y1="13" x2="8" y2="13"></line>
									<line x1="16" y1="17" x2="8" y2="17"></line>
									<polyline points="10 9 9 9 8 9"></polyline>
								{:else if item.icon === 'bar-chart'}
									<!-- Results icon -->
									<line x1="18" y1="20" x2="18" y2="10"></line>
									<line x1="12" y1="20" x2="12" y2="4"></line>
									<line x1="6" y1="20" x2="6" y2="14"></line>
								{:else}
									<!-- Settings icon -->
									<circle cx="12" cy="12" r="3"></circle>
									<path
										d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"
									></path>
								{/if}
							</svg>
						</span>
						{#if !isCollapsed}
							<span class="ml-3">{item.title}</span>
						{/if}
					</a>
				</li>
			{/each}
		</ul>
	</nav>

	<!-- Footer with recent items -->
	{#if !isCollapsed}
		<div class="border-surface-700 border-t p-4">
			<h3 class="mb-2 text-sm font-medium text-white">Recent Items</h3>
			<ul class="space-y-1 text-sm">
				<li>
					<a href="/results/last" class="text-secondary-300 hover:text-white">Last Benchmark</a>
				</li>
				<li>
					<a href="/categories/coding" class="text-secondary-300 hover:text-white"
						>Coding Category</a
					>
				</li>
			</ul>
		</div>
	{/if}
</aside>
