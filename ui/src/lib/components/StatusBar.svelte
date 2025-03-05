<script lang="ts">
  import { onMount } from 'svelte';
  
  // Props for the component
  let { activeModel, currentOperation } = $props<{
    activeModel?: string;
    currentOperation?: string;
  }>();
  
  // State for system info
  let systemStatus = $state("Ready");
  let cpuUsage = $state(0);
  let memoryUsage = $state(0);
  let currentTime = $state(new Date().toLocaleTimeString());
  
  // Update time every second
  onMount(() => {
    const interval = setInterval(() => {
      currentTime = new Date().toLocaleTimeString();
      
      // In a real implementation, we would fetch these values from an API
      // These are mock values for demonstration
      cpuUsage = Math.floor(Math.random() * 40) + 10; // 10-50% CPU usage
      memoryUsage = Math.floor(Math.random() * 30) + 20; // 20-50% memory usage
    }, 1000);
    
    return () => {
      clearInterval(interval);
    };
  });
</script>

<footer class="flex items-center justify-between px-4 py-2 bg-surface-900 border-t border-surface-700 text-white text-sm">
  <div class="flex items-center space-x-4">
    <div class="flex items-center">
      <span class="text-surface-300 mr-2">Status:</span>
      <span class="text-success-400 font-medium">{systemStatus}</span>
    </div>
    
    {#if activeModel}
      <div class="flex items-center">
        <span class="text-surface-300 mr-2">Model:</span>
        <span>{activeModel}</span>
      </div>
    {/if}
    
    {#if currentOperation}
      <div class="flex items-center">
        <span class="text-surface-300 mr-2">Operation:</span>
        <span>{currentOperation}</span>
      </div>
    {/if}
  </div>
  
  <div class="flex items-center space-x-4">
    <div class="flex items-center">
      <span class="text-surface-300 mr-2">CPU:</span>
      <div class="w-24 bg-surface-700 rounded-full h-2 mr-1">
        <div class="bg-primary-400 h-2 rounded-full" style="width: {cpuUsage}%"></div>
      </div>
      <span>{cpuUsage}%</span>
    </div>
    
    <div class="flex items-center">
      <span class="text-surface-300 mr-2">Memory:</span>
      <div class="w-24 bg-surface-700 rounded-full h-2 mr-1">
        <div class="bg-secondary-400 h-2 rounded-full" style="width: {memoryUsage}%"></div>
      </div>
      <span>{memoryUsage}%</span>
    </div>
    
    <div>
      {currentTime}
    </div>
  </div>
</footer>