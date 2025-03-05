<script lang="ts">
	let isCollapsed = $state(false);
	let { title, hasContent, children } = $props<{
		title?: string;
		hasContent?: boolean;
		children?: any;
	}>();

	let showPanel = $derived(!isCollapsed && (hasContent ?? true));

	function togglePanel(): void {
		isCollapsed = !isCollapsed;
	}
</script>

<aside
	class="bg-surface-800 border-surface-700 flex h-full flex-col border-l transition-all duration-300 {isCollapsed
		? 'w-0 overflow-hidden'
		: 'w-80'}"
>
	{#if !isCollapsed}
		<div class="border-surface-700 flex items-center justify-between border-b p-4">
			<h2 class="text-lg font-semibold text-white">{title || 'Configuration'}</h2>
			<button
				onclick={togglePanel}
				class="hover:bg-surface-700 rounded-md p-1.5 text-white"
				aria-label="Collapse panel"
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
					<polyline points="15 18 9 12 15 6"></polyline>
				</svg>
			</button>
		</div>

		<div class="flex-1 overflow-y-auto p-4">
			<!-- Default content when nothing is selected -->
			{#if !hasContent}
				<div class="text-surface-300 flex h-full flex-col items-center justify-center text-center">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						width="48"
						height="48"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="1"
						stroke-linecap="round"
						stroke-linejoin="round"
					>
						<circle cx="12" cy="12" r="10"></circle>
						<line x1="12" y1="8" x2="12" y2="12"></line>
						<line x1="12" y1="16" x2="12.01" y2="16"></line>
					</svg>
					<p class="mt-4">Select an item to view its details and configuration options</p>
				</div>
			{/if}
			{@render children()}
		</div>
	{:else}
		<button
			onclick={togglePanel}
			class="bg-surface-800 border-surface-700 absolute right-0 top-1/2 -translate-y-1/2 rounded-l-md border border-r-0 p-1.5 text-white"
			aria-label="Expand panel"
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
			>
				<polyline points="9 18 15 12 9 6"></polyline>
			</svg>
		</button>
	{/if}
</aside>
