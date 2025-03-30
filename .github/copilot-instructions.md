# **AI Assistant Coding Guidelines**

**Purpose:** These guidelines aim to ensure code consistency, maintainability, quality, and collaboration across our Python (FastAPI) and Svelte 5 + TypeScript projects. Adhering to these standards helps us build robust and scalable applications.

**Review & Updates:** These guidelines will be reviewed periodically (e.g., quarterly or as major dependencies change) and updated as needed. Feedback and suggestions for improvement are welcome.

# Python
## File Structure

Organize code into logical modules:

*   `main.py`: Application entry point (FastAPI app initialization, middleware, startup/shutdown events).
*   `config.py`: Configuration loading and settings model (using Pydantic).
*   `routes/`: Directory containing route modules (e.g., `routes/users.py`, `routes/items.py`). Use FastAPI `APIRouter`.
*   `services/`: Business logic layer, orchestrating operations.
*   `repositories/`: Data access layer (database interactions, external API clients).
*   `models.py`: Core internal data structures (Pydantic `BaseModel` representing domain entities, potentially database-aligned if not using ORM models directly).
*   `schemas.py`: API request/response validation models (Pydantic `BaseModel`, often tailored for specific endpoints, may inherit/compose from `models.py`).
*   `enums.py`: Application-specific Enum classes.
*   `exceptions.py`: Custom exception classes.
*   `utils.py`: General utility functions not specific to any layer.
*   `constants.py`: Non-enum constant values (if necessary, prefer Enums where appropriate).
*   `tests/`: Directory for automated tests (structure mirroring the application).

## Code Style

*   **Version:** Use Python 3.12+.
*   **Type Hints:**
    *   Mandatory for all function/method signatures (arguments and return types).
    *   Use modern type hints:
        *   `|` for union types (e.g., `int | str`).
        *   **`Type | None`** instead of `Optional[Type]` (e.g., `str | None`).
        *   Use built-in generics (`list[int]`, `dict[str, Any]`) instead of `typing.List`, `typing.Dict`.
        *   Use `TypeVar` and `typing.Generic` for creating generic functions and classes.
*   **Docstrings:**
    *   Use **Google Style** docstrings for modules, classes, functions, and methods.
    *   Document non-obvious logic, algorithms, and the *purpose* of complex code sections.
*   **Comments:**
    *   Use sparingly. Explain *why* something is done, not *what* is done if the code is self-explanatory.
    *   Avoid commented-out code; use version control instead.

## Logging

- Use structured logging with extra fields
- Include contextual information in logs
- Use appropriate log levels.
- Include correlation IDs for request tracing

## Data Models

*   **Version:** Use Pydantic v2.10+.
*   **Usage:** Use Pydantic `BaseModel` for structured data representation, validation, and serialization (API schemas, configuration, complex data structures). Prefer them over raw dictionaries for these purposes.
*   **Type Hints:** Always include explicit field type hints.
*   **Validation:** Leverage built-in and custom validators (`@field_validator` in v2) for data integrity.
*   **Metadata:** Use `Field()` for default values, descriptions, examples, validation constraints (e.g., `min_length`, `max_length`, `gt`, `lt`).
*   **Enums:** Use `enum.Enum` classes (defined in `enums.py`) for fields with a fixed set of choices, instead of raw strings or constants.
*   **Configuration:** Utilize `model_config` (Pydantic v2) for settings like:
    *   `extra = 'forbid'` (recommended to prevent unexpected fields).
    *   `frozen = True` (for immutable models where appropriate).
    *   `from_attributes = True` (if mapping from ORM objects or other attribute-based classes).

## Naming Conventions

*   `snake_case`: Variables, functions, methods, modules, package directories.
*   `PascalCase`: Classes (including Pydantic models, custom exceptions).
*   `UPPER_SNAKE_CASE`: Constants (defined in `constants.py` or at module level).
*   `_leading_underscore`: Internal/private attributes or methods (by convention).
*   **Suffixes:**
    *   Consider suffixing Enums with `Enum` (e.g., `StatusEnum`).
    *   Consider suffixing API schemas in `schemas.py` with `Schema` (e.g., `UserCreateSchema`) to distinguish from internal models. Avoid generic `Model` suffixes unless necessary for clarity.
*   **Loggers:** Use descriptive logger names, typically based on the module path (e.g., `logging.getLogger(__name__)`).

## Error Handling

*   **Custom Exceptions:** Define custom, specific exception types inheriting from a common base exception (e.g., `AppBaseException(Exception)`) in `exceptions.py`.
*   **Explicit Handling:** Catch specific exceptions rather than generic `Exception`.
*   **Context:** Include informative error messages and relevant context when raising or handling exceptions.
*   **FastAPI Error Handling:** Use FastAPI's exception handlers (`@app.exception_handler`) to translate custom exceptions into standardized HTTP error responses (e.g., consistent JSON error structure).
*   **Validation Errors:** Let Pydantic validation errors propagate to FastAPI's default handler or a custom handler to return 422 responses.
*   **Logging:** Log exceptions appropriately, including stack traces for unexpected errors (ERROR level) and potentially handled exceptions (WARNING or INFO level, depending on severity).
*   **Context Managers:** Use `try...finally` or context managers (`with` statement) for reliable resource cleanup (e.g., database connections, file handles).


# Svelte 5 + TypeScript

## State Management
*   **Core:**
    *   Use `$state<Type>(initialValue)` for reactive state variables.
    *   Use `$derived<Type>(expression)` for computed values derived from state or props.
    *   Use `$effect(() => { ... })` for side effects reacting to state/prop changes (e.g., data fetching, subscriptions, manual DOM). Runs *after* DOM updates by default. Use `$effect.pre` if effects must run *before* DOM updates.
    *   Use `$props<{propName: Type}>()` to declare component properties with types.
*   **Debugging:** Use `$inspect(value)` to log rune value changes during development.

## Component Context Pattern
*   **Pattern:** Use Svelte's `setContext` / `getContext` for dependency injection or passing state down deeply nested component trees *sparingly*.
    ```ts
    // Parent: Provide reactive context access
    import { setContext } from 'svelte';
    let count = $state(0);
    setContext('myKey', {
      get count() { return count; },
      set count(v) { count = v; }
    });

    // Child: Access context
    import { getContext } from 'svelte';
    const ctx = getContext<{ count: number }>('myKey');
    // Read: $derived(ctx.count) or inside $effect/functions
    // Write: ctx.count = newValue;
    ```
*   **Key:** Use a unique `Symbol` or a well-namespaced string constant for the context key.
*   **Caution:** Prefer props or stores for most state sharing. Use mutable context only when necessary and clearly documented.


## Event Handling

*   **DOM Events:** Use the shorthand `onclick={handler}` (preferred), `oninput`, `onkeydown`, etc.
*   **Component Events:** Define component event handlers using `onEventName={handler}` when using the component (requires the component to dispatch the event). Use `createEventDispatcher` if needed for non-rune components or specific patterns.

## Component Structure
`Follow this general order within the script block for consistency:

```svelte
<script lang="ts">
  // 1. Imports (Svelte, Libs, Components, Types)
  import { getContext } from 'svelte';
  import type { SomeType } from '$lib/types/someType';
  import ChildComponent from '$lib/components/ChildComponent.svelte';
  import { apiService } from '$lib/services/api';

  // 2. Type Definitions (Local types if necessary)
  type ComponentState = 'loading' | 'error' | 'loaded' | 'empty';

  // 3. Props (Using $props)
  let { initialId = null }: { initialId: string | null } = $props();

  // 4. Context (Using getContext)
  const userContext = getContext<UserContextType>('user');

  // 5. State (Using $state)
  let items = $state<SomeType[]>([]);
  let selectedItem = $state<SomeType | null>(null);
  let isLoading = $state(true);
  let errorMessage = $state<string | null>(null);

  // 6. Derived State (Using $derived)
  let itemCount = $derived(items.length);
  let hasItems = $derived(itemCount > 0);
  let componentState = $derived<ComponentState>(() => {
    if (isLoading) return 'loading';
    if (errorMessage) return 'error';
    if (!hasItems) return 'empty';
    return 'loaded';
  });

  // 7. Effects (Using $effect, $effect.pre)
  $effect(() => {
    // Fetch data when initialId changes
    if (initialId) {
      loadItem(initialId);
    }
  });

  // 8. Functions (Event Handlers, Logic, API calls)
  async function loadItems() {
    isLoading = true;
    errorMessage = null;
    try {
      items = await apiService.getItems();
    } catch (e) {
      errorMessage = e instanceof Error ? e.message : 'Failed to load items';
      // TODO: Log the full error `e`
    } finally {
      isLoading = false;
    }
  }

  function handleSelectItem(item: SomeType) {
    selectedItem = item;
  }

  // 9. Initialization (Run initial logic, often via $effect or direct calls)
  loadItems(); // Initial load

</script>

<!-- Markup using defined state/logic -->
```

## UI States
Handle common UI states explicitly within components:

*   **Loading:** Show a clear loading indicator (e.g., centered spinner, skeleton layout). Use `isLoading` state.
*   **Error:** Display a user-friendly error message (from `errorMessage` state) with potentially a retry action. Use a distinct visual style (e.g., red box).
*   **Empty:** When data loads successfully but is empty (`!hasItems`), show an informative message, potentially with an icon and a call-to-action (e.g., "No items found. Create one?").
*   **Content:** Display the main content (lists, forms, details) when data is loaded successfully and is not empty.

Use Svelte's control flow blocks (`{#if}`, `{#each}`, `{#await}`) effectively to render these states.
## CRUD Pattern
Standardize Create, Read, Update, Delete operations:

```ts
// State: (Assuming items, isLoading, errorMessage are defined as $state)

// Read (Load All)
async function load() {
  isLoading = true;
  errorMessage = null;
  try {
    items = await apiService.getItems();
  } catch (e) {
    errorMessage = e instanceof ApiError ? e.message : 'Failed to load items';
    console.error("Load error:", e); // Log full error
  } finally {
    isLoading = false;
  }
}

// Create / Update (Save)
async function saveItem(data: ItemData, id?: string) {
  // Consider adding loading/disabled state to the form
  try {
    if (id) { // Update
      const updatedItem = await apiService.updateItem(id, data);
      items = items.map(item => item.id === id ? updatedItem : item);
    } else { // Create
      const newItem = await apiService.createItem(data);
      items = [...items, newItem];
    }
    // Optional: Show success message, close modal, etc.
  } catch (e) {
    // Show error message specific to the save operation
    console.error("Save error:", e);
  } finally {
    // Reset form loading state
  }
}

// Delete
async function deleteItem(id: string) {
  // Optional: Add confirmation dialog
  // Optional: Add local loading state for the specific item being deleted
  try {
    await apiService.deleteItem(id);
    items = items.filter(item => item.id !== id);
    // Optional: Show success message
  } catch (e) {
    // Show error message specific to the delete operation
    console.error("Delete error:", e);
  } finally {
    // Reset item loading state
  }
}
```

## Use modern control structures:
*   Use `{#if condition} ... {:else if condition2} ... {:else} ... {/if}` for conditional rendering. Avoid redundant checks.
*   Use `{#each items as item (item.id)} ... {/each}` for lists. **Always use a unique key** `(item.id)` for performance and correct updates.
*   Use `{#await promise} ... {:then value} ... {:catch error} ... {/await}` for handling promises directly in the markup when appropriate.

## Component Structure:

*   **Granularity:** One logical component per `.svelte` file. Keep components focused on a single responsibility.
*   **Naming:** Use `PascalCase` for component filenames (e.g., `UserProfileCard.svelte`).
*   **Location:** Group components by feature or domain within `$lib/components/` (e.g., `$lib/components/user/`, `$lib/components/shared/`).

## Adapter
- Use static adapter for server-side rendering

## TypeScript Configuration
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

## Types and Interfaces

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
## Error Handling

- Use try/catch blocks for async operations
- Display error states in UI
- Use error boundaries where appropriate
- Log errors with context

## Performance

*   **Code Splitting:** Use dynamic `import()` to lazy-load components or libraries that are not needed immediately (e.g., modals, heavy libraries, components below the fold).
*   **List Virtualization:** Implement virtual scrolling for very long lists to render only visible items.
*   **Effects:** Optimize `$effect` dependencies to avoid unnecessary re-runs.
*   **Transitions:** Use Svelte's `transition:`, `animate:`, and `in:/out:` directives judiciously for UI polish, being mindful of performance impact.

## Accessibility:

*   **Semantic HTML:** Use appropriate HTML elements (`<nav>`, `<button>`, `<main>`, `<article>`, etc.) for their intended purpose.
*   **ARIA Attributes:** Add necessary ARIA roles and attributes (`role`, `aria-label`, `aria-required`, `aria-hidden`, etc.) where semantic HTML is insufficient, especially for custom interactive components.
*   **Keyboard Navigation:** Ensure all interactive elements are focusable and operable via keyboard.
*   **Focus Management:** Manage focus logically, especially in modals and dynamic interfaces.
*   **Testing:** Regularly test with automated tools (`axe-core` via browser extensions or test integrations) and perform manual testing using keyboard navigation and screen readers.

## Security:

- CSP headers configuration
- Sanitize user input in forms
- Use SvelteKit's security hooks

## Component Variants

-*   **Dynamic Classes:** Use object lookups or utility functions for applying conditional classes based on props (variants, sizes, states).
    ```typescript
    // Example within <script>
    type ButtonVariant = 'primary' | 'secondary' | 'danger';
    const variantClasses: Record<ButtonVariant, string> = { /* ... */ };
    export let variant: ButtonVariant = 'primary';

    // Example using clsx or tailwind-merge (install library first)
    import clsx from 'clsx';
    export let disabled = false;
    // In markup: class={clsx(baseClasses, variantClasses[variant], { 'opacity-50 cursor-not-allowed': disabled })}
    ```
*   **Utility Libraries:** Consider using `clsx` or `tailwind-merge` for cleaner conditional class logic.
*   **Tailwind:**
    *   **Theme:** Strictly use colors, spacing, fonts, etc., defined in `tailwind.config.ts`. Avoid hardcoding theme values (e.g., `#FF0000` or `13px`).
    *   **`@apply`:** Use `@apply` sparingly in CSS files, primarily for extracting highly repeated component patterns. Prefer applying utility classes directly in the markup.
    *   **Arbitrary Values:** Use Tailwind's arbitrary values (e.g., `mt-[13px]`) only when the design system doesn't cover a specific requirement and it cannot be reasonably added to the theme.

## Responsive Design

*   **Scope:** The primary target is desktop design.
*   **Adaptability:** Ensure designs adapt fluidly across common desktop resolutions (e.g., from 1280px width upwards). Use responsive modifiers (e.g., `md:`, `lg:`) as needed, even within the desktop range if necessary for layout adjustments.

## Performance

- Use @apply sparingly, prefer inline classes
- Consider extracting commonly repeated patterns
- Use arbitrary values only when necessary

## Theme Configuration
- Always use colors from tailwind.config.ts and do not hardcode colors
- Do not change the default Tailwind color palette