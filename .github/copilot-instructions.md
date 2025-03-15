
# GitHub Copilot Instructions

## Python
### File Structure
- utils.py for utility functions
- models.py for Pydantic models
- enums.py for Enum classes
- services.py for business logic
- repositories.py for data access
- exceptions.py for custom exceptions
- main.py for application entry point
- schemas.py for request/response schemas
- config.py for configuration settings
- routes.py for FastAPI route definitions

### Code Style

- Use Python 3.12+ type hints with | for union types. 
- Do not use Dict and List from typing module, use the built-in dict and list.
- Use TypeVar and Generic for generic type hints
- Always include return type hints
- Use None instead of Optional
- Ensure that all code, especially complex logic, is well-documented. Include comments for non-trivial code blocks.

### Code Comments
- Use Comments Sparingly: Comments should explain why something is done, not what is done. Avoid commenting on obvious code.
- Complex Logic: For complex algorithms or non-trivial logic, include comments that explain the reasoning and steps involved.

### Logging

- Use structured logging with extra fields
- Include contextual information in logs
- Use appropriate log levels.
- Include correlation IDs for request tracing

### Data Models

- Use Pydantic BaseModel instead of dictionaries and modern Pydantic functionality like model_dump() instead of dict()
- Use Enum classes instead of constants or string literals
- Always include field type hints in models
- Use model validation and custom validators where appropriate
- Use Field() for additional metadata and validation
- Use model config for common settings

### Naming Conventions

- Use snake_case for functions and variables
- Use PascalCase for classes and models
- Suffix enums with 'Enum' (e.g., StatusEnum)
- Suffix models with 'Model' (e.g., UserModel)
- Prefix private attributes with single underscore
- Use descriptive logger names based on module path

### Error Handling

- Use explicit exception types
- Include error messages
- Add context managers where appropriate
- Use Pydantic validation errors for data validation


## Svelte 5 + TypeScript

### State Management
- Use `$state<Type>(initialValue)` for reactive state
- Use `$derived` for computed values
- Use `$effect(() => {})` for side effects
- Use `$props<{prop: Type}>()` for props with types

### Component Context Pattern
```ts
// Setting context in parent
const contextObj = { get prop() { return prop; }, set prop(v) { prop = v; } };
setContext('key', contextObj);

// Using in child
const ctx = getContext('key');
ctx.prop = newValue;
```

### Event Handling
- Use `onclick={handler}` not `on:click`
- Components: `onEventName={handler}`

### Component Structure
```svelte
<script lang="ts">
  // 1. Imports
  import { getContext } from 'svelte';
  import ComponentA from '$lib/components/path/ComponentA.svelte';
  
  // 2. TypeDefs
  type Entity = { id: string; /* props */ };
  
  // 3. Context
  const ctx = getContext('key');
  
  // 4. State
  let items = $state<Entity[]>([]);
  let selected = $state<Entity|null>(null);
  let isLoading = $state(true);
  let error = $state<string|null>(null);
  
  // 5. Derived
  let hasItems = $derived(items.length > 0);
  
  // 6. Effects
  $effect(() => { updatePanel(); });
  
  // 7. Functions
  async function load() { /* fetch */ }
  function updatePanel() { /* update context */ }
  
  // 8. Initialization
  load();
</script>

<div class="space-y-6">
  <!-- Header + Action -->
  <div class="flex justify-between items-center">
    <h1 class="text-2xl font-bold">Title</h1>
    <button 
      onclick={addNew}
      class="px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-md">
      New Item
    </button>
  </div>
  
  {#if isLoading}
    <!-- Loading spinner -->
  {:else if error}
    <!-- Error message + retry -->
  {:else if !hasItems}
    <!-- Empty state -->
  {:else}
    <!-- Content -->
  {/if}
</div>
```

### UI States
- Loading: Centered spinner
- Error: Red box with retry button
- Empty: Icon + description + action button
- Content: Lists/forms with actions

### CRUD Pattern
```ts
// Load
async function load() {
  try {
    isLoading = true;
    error = null;
    items = await apiService.getItems();
  } catch (e) {
    error = e instanceof Error ? e.message : 'Failed';
  } finally {
    isLoading = false;
  }
}

// Create/Update
async function saveItem() {
  if (selected?.id) {
    const updated = await apiService.update(id, data);
    items = items.map(i => i.id === id ? updated : i);
  } else {
    const created = await apiService.create(data);
    items = [...items, created];
  }
}

// Delete
async function deleteItem(id) {
  await apiService.delete(id);
  items = items.filter(i => i.id !== id);
}
```

### Use modern control structures:
- {#if} without redundant conditions
- {#each} with keyed items
- {#await} for promise handling

### Component Structure:
- One component per file
- Keep components small and focused
- Use PascalCase for component names
- Suffix component files with .svelte
- Place components in feature-based directories

### Adapter
- Use static adapter for server-side rendering

### TypeScript Configuration
```typescript
// tsconfig.json
{
	"extends": "./.svelte-kit/tsconfig.json",
	"compilerOptions": {
		"strict": true,
		"moduleResolution": "bundler",
		"allowImportingTsExtensions": true,
		"noImplicitAny": true,
		"noImplicitThis": true,
		"strictNullChecks": true,
		"strictFunctionTypes": true,
		"strictBindCallApply": true,
		"alwaysStrict": true,
		"exactOptionalPropertyTypes": true
	}
}
```

### Types and Interfaces

- Place shared types in dedicated files
- Use discriminated unions for state management
- Define prop types explicitly
- Use type predicates for type narrowing

```typescript
// types/user.ts
export type User = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
};

export enum UserRole {
  Admin = 'ADMIN',
  User = 'USER',
  Guest = 'GUEST',
}

// types/states.ts
export type LoadingState = {
  data: T | null;
  isLoading: boolean;
  error: string | null;
};
```
### Error Handling

- Use try/catch blocks for async operations
- Display error states in UI
- Use error boundaries where appropriate
- Log errors with context

### Performance

- Lazy load non-critical components
- Use Svelte's animate and transition directives
- Implement virtual scrolling for long lists

### Accessibility:

- Required ARIA attributes
- Semantic HTML elements

### Security:

- CSP headers configuration
- Sanitize user input in forms
- Use SvelteKit's security hooks

### Component Variants

- Use dynamic classes with TypeScript types
- Create reusable variant patterns
- Use template literals for conditional classes

```typescript
<script lang="ts">
  type ButtonVariant = 'primary' | 'secondary' | 'danger';
  type ButtonSize = 'sm' | 'md' | 'lg';

  export let variant: ButtonVariant = 'primary';
  export let size: ButtonSize = 'md';

  const variantClasses: Record<ButtonVariant, string> = {
    primary: 'bg-blue-500 hover:bg-blue-600 text-white',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-800',
    danger: 'bg-red-500 hover:bg-red-600 text-white',
  };

  const sizeClasses: Record<ButtonSize, string> = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
</script>

<button class="
  /* Base styles */
  flex items-center justify-center rounded-md transition-all
  /* Dynamic variants */
  {variantClasses[variant]}
  {sizeClasses[size]}
">
  <slot />
</button>
```

### Responsive Design

- Only desktop design is required
- Ensure designs adapt correctly to various desktop resolutions

### Performance

- Use @apply sparingly, prefer inline classes
- Consider extracting commonly repeated patterns
- Use arbitrary values only when necessary

### Theme Configuration
- Always use colors from tailwind.config.ts and do not hardcode colors
- Do not change the default Tailwind color palette