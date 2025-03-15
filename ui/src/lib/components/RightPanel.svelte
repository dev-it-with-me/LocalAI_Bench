<script lang="ts">
	import { setContext } from 'svelte';
	import { browser } from '$app/environment';

	let isCollapsed = $state(false);
	let { title, hasContent, children } = $props<{
		title?: string;
		hasContent?: boolean;
		children?: () => any;
	}>();

	// Default width in pixels (80 in Tailwind is 20rem, which is ~320px)
	let minWidth = 320;
	let panelWidth = $state(minWidth);
	let isResizing = $state(false);
	let startX = 0;
	let startWidth = 0;
	let panelElement: HTMLElement;

	let showPanel = $derived(!isCollapsed && (hasContent ?? true));

	function togglePanel(): void {
		isCollapsed = !isCollapsed;
	}

	// Get the dynamic component and props
	let component = $derived(children ? children()?.component : null);
	let componentProps = $derived(children ? children()?.props : {});

	// Automatically expand panel when component or props change
	$effect(() => {
		if (component !== null || Object.keys(componentProps).length > 0) {
			isCollapsed = false;
		}
	});

	// Update panel width using CSS variable when width changes
	$effect(() => {
		if (panelElement && !isCollapsed) {
			panelElement.style.setProperty('--panel-width', `${panelWidth}px`);
		}
	});

	// Start resizing
	function startResize(event: MouseEvent) {
		isResizing = true;
		startX = event.clientX;
		startWidth = panelWidth;
		
		// Prevent text selection during resize
		document.body.style.userSelect = 'none';
		
		// Remove transition during resize for better performance
		if (panelElement) {
			panelElement.classList.add('resizing');
		}
		
		// Add event listeners for mouse movement and release
		if (browser) {
			document.addEventListener('mousemove', handleMouseMove);
			document.addEventListener('mouseup', stopResize);
		}
	}
	
	// Handle mouse movement during resize using requestAnimationFrame for better performance
	function handleMouseMove(event: MouseEvent) {
		if (!isResizing) return;
		
		requestAnimationFrame(() => {
			const diff = startX - event.clientX;
			const newWidth = Math.max(minWidth, startWidth + diff);
			panelWidth = newWidth;
		});
	}
	
	// Stop resizing
	function stopResize() {
		isResizing = false;
		document.body.style.userSelect = '';
		
		// Restore transition after resize
		if (panelElement) {
			panelElement.classList.remove('resizing');
		}
		
		if (browser) {
			document.removeEventListener('mousemove', handleMouseMove);
			document.removeEventListener('mouseup', stopResize);
		}
	}
</script>

<aside
	bind:this={panelElement}
	class="bg-surface-800 border-surface-700 flex h-full flex-col border-l relative {isCollapsed
		? 'w-0 overflow-hidden'
		: 'panel-width'}"
>
	{#if !isCollapsed}
		<!-- Resize handle -->
		<div 
			class="absolute left-0 top-0 w-1 h-full cursor-ew-resize hover:bg-surface-500 z-10"
			onmousedown={startResize}
		></div>
		
		<!-- Header - Fixed at the top -->
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

		<!-- Content Container - Takes remaining height with independent scrolling -->
		<div class="flex-1 overflow-hidden flex flex-col">
			<div class="flex-1 overflow-y-auto overflow-x-hidden p-4 panel-content">
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
				{:else if component}
					<!-- Render dynamic component using svelte:component -->
					<svelte:component this={component} {...componentProps} />
				{/if}
			</div>
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

<style>
	/* Use CSS variables for better performance */
	.panel-width {
		width: var(--panel-width, 320px);
		transition: width 0.3s ease;
	}
	
	/* Remove transition during active resizing for better performance */
	.resizing {
		transition: none !important;
	}
	
	/* Ensure panel content is independently scrollable */
	.panel-content {
		height: 100%;
		max-height: 100%;
	}
</style>
