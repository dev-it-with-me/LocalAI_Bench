# LocalAI Bench
Your personal AI benchmarking tool.

## Introduction
LocalAI Bench is a benchmarking tool for AI models. It provides a platform to evaluate and compare different AI models based on various tasks and categories. It supports multiple AI models from Hugging Face hub via custom implementation or Ollama API. It also supports models from other API providers.

## Goal
The goal of LocalAI Bench is to provide a platform to evaluate and compare different AI models based on various tasks which are useful for the user.

It not aims to compare SOTA models, but a locally available models which are useful in a stituation where API usage is not recommended choise - like in a corporate environment, where data privacy is a concern or to reduce the cost of API usage.

Unlike other benchmarking tools, LocalAI Bench is not to provide a score on a general field, like Math, Physics or reasoning capabilites, but to compare AI models in categories usefull for the user like:
- specific document types understanding,
- agentic usage in a unique enterprise process,
- coding tasks on a specific language or framework or event corporate coding standards.


## Categories of benchmarks:
There is no limit to the number of categories and tasks that can be added to LocalAI Bench. The first version of LocalAI Bench will contain 3 default categories:

- Coding specific to User Interface (Vision)
  - Example tasks: Implement change in the  UI components based on the user graphical instructions.
- Corporate Document Understanding
  - Example tasks: Extract information from invoices in specific format; summarize legal documents; classify internal documents based on few examples.
- Agentic usage in recruitment process
  - Example tasks: Automate candidate screening workflows; generate personalized 
    candidate feedback.


## Scoring
For each category, there are multiple tasks with different complexity levels and scoring criteria.
Scoring criteria now include:
- Time Score: Time taken to complete the task, normalized in the range [0.8, 1.2].
- Quality Score: How good the solution is based on user judgment or provided ground truth (scale 1 to 10).
- Complexity Score: Complexity of the task (scale 1 to 5).
- Cost Factor: A normalized metric representing the cost of executing the task.
- Memory Usage Factor: A normalized metric measuring memory consumption.

Configurable weights allow users to prioritize components for every task/category. A proposed formula is:

Ultimate Score = (Time Score * w_time) *
                 (Quality Score * w_quality) *
                 (Complexity Score * w_complexity) *
                 (Cost Factor * w_cost) *
                 (Memory Usage Factor * w_memory)

Users can adjust the weights (w_time, w_quality, w_complexity, w_cost, w_memory)
to tailor the scoring model based on operational and resource constraints.

### Automated Evaluation
For objective measurement of Quality Score, the system will implement:
- Unit test validations for coding tasks
- Ground truth comparison for document understanding
- Rule-based evaluation for recruitment process tasks
- Manual review option with structured rubrics for subjective assessment

### Dashboard
The dashboard provides a summary of the scores for each model in each category, with:
- Comparative visualizations (radar charts, bar graphs)
- Detailed performance breakdowns by category and task
- Historical performance tracking
- Export functionality for reports

## Supported Models
- Model filtering by task compatibility

### Hugging Face
- Support for transformers library models
- Integration with Hugging Face Hub API by manual implementation model adapter for each model
- Configuration options for model parameters
- Local deployment instructions

### Ollama
- Support for all compatible Ollama models
- Configuration options for model parameters
- Local deployment instructions

### API Providers
- OpenAI (GPT series)
- Anthropic (Claude models)
- Custom API integration framework
- Secure credential management

## Benchmarking Structure

### Category-Level Benchmarking
- Primary benchmarking is performed at the category level
- Results and scores are aggregated across all tasks in a category
- Models are primarily compared by their performance in entire categories
- Category reports show overall performance metrics with drill-down capabilities

### Task-Level Benchmarking
- Individual tasks can be run separately as needed
- Custom task lists can be defined for specialized comparisons
- Task-specific metrics are recorded and available in detailed reports
- Task-level comparison available through filtering options in the dashboard

## Task Templates

Task templates provide standardized structures for creating comparable benchmarking tasks. They ensure consistency and reduce setup time.

### Template Structure
```json
{
  "template_id": "code-ui-component-update",
  "name": "UI Component Update Task",
  "category": "coding_ui_vision",
  "description": "Task for updating UI components based on visual instructions",
  "input_schema": {
    "component_description": "string",
    "current_code": "string",
    "visual_instructions": "image_path",
    "expected_behavior": "string"
  },
  "evaluation_criteria": {
    "functional_correctness": {"weight": 0.4, "type": "unit_test"},
    "visual_accuracy": {"weight": 0.3, "type": "manual_review"},
    "code_quality": {"weight": 0.2, "type": "static_analysis"},
    "performance": {"weight": 0.1, "type": "benchmark"}
  },
  "output_schema": {
    "updated_code": "string",
    "explanation": "string"
  },
  "test_cases": [
    {"input": "test_inputs/ui_update_1.json", "expected": "test_expected/ui_update_1.json"}
  ]
}
```

### Example Templates

1. **Document Information Extraction Template**
```json
{
  "template_id": "invoice-extraction",
  "name": "Invoice Information Extraction",
  "category": "document_understanding",
  "description": "Extract key fields from invoices",
  "input_schema": {
    "document_image": "image_path",
    "target_fields": ["invoice_number", "date", "total_amount", "vendor_name"]
  },
  "evaluation_criteria": {
    "field_accuracy": {"weight": 0.7, "type": "ground_truth_comparison"},
    "processing_speed": {"weight": 0.3, "type": "time_measurement"}
  },
  "output_schema": {
    "extracted_fields": "json_object"
  }
}
```

2. **Recruitment Screening Template**
```json
{
  "template_id": "resume-screening",
  "name": "Resume Screening Task",
  "category": "recruitment_process",
  "description": "Screen resumes for job fit",
  "input_schema": {
    "resume": "text",
    "job_description": "text",
    "required_skills": "string_array",
    "preferred_qualifications": "string_array"
  },
  "evaluation_criteria": {
    "candidate_ranking": {"weight": 0.5, "type": "ground_truth_comparison"},
    "justification_quality": {"weight": 0.5, "type": "manual_review"}
  },
  "output_schema": {
    "fit_score": "number",
    "skill_matches": "string_array",
    "missing_skills": "string_array",
    "recommendation": "string",
    "justification": "string"
  }
}
```

## Data Storage and Sharing

### JSON Data Structure
LocalAI Bench uses JSON files for data storage to facilitate easy sharing of benchmarks and results:

```
/data
  /categories
    coding_ui_vision.json
    document_understanding.json
    recruitment_process.json
  /tasks
    task_id_1.json
    task_id_2.json
    task_id_3.json
  /templates
    code-ui-component-update.json
    invoice-extraction.json
    resume-screening.json
  /models
    model_id_1.json
    model_id_2.json
  /results
    benchmark_run_id_1.json
    benchmark_run_id_2.json
```

### Export/Import Functionality

The export/import system allows users to share benchmarks, tasks, and results with others:

#### Export Types
- **Full Benchmark Suite**: Complete export of categories, tasks, templates, and configurations
- **Category Export**: Export a specific category with all its tasks and templates
- **Task Set Export**: Export a custom set of tasks across categories
- **Results Export**: Export benchmark results for sharing or analysis

#### Import Capabilities
- **Benchmark Suite Import**: Import a complete benchmark suite from another user
- **Category Import**: Add a new category with all associated tasks
- **Task Import**: Import individual tasks into existing categories
- **Results Import**: Import benchmark results for comparison

#### Export Example
```json
{
  "export_type": "category",
  "export_date": "2023-10-15T14:30:00Z",
  "version": "1.0",
  "content": {
    "category": {
      "id": "document_understanding",
      "name": "Corporate Document Understanding",
      "description": "Benchmarks for document understanding tasks"
    },
    "tasks": [
      {"id": "task1", "name": "Invoice Extraction", "template_id": "invoice-extraction", "...": "..."},
      {"id": "task2", "name": "Contract Analysis", "template_id": "contract-analysis", "...": "..."}
    ],
    "templates": [
      {"id": "invoice-extraction", "...": "..."},
      {"id": "contract-analysis", "...": "..."}
    ]
  }
}
```

#### Import Process
1. User selects import file
2. System validates the structure and content
3. User reviews what will be imported
4. System checks for conflicts
5. User resolves any conflicts
6. System imports the selected components
7. Imported items are immediately available for use

## Implementation Notes
### Backend Architecture
- Python 3.12+ with FastAPI
  - Modular structure with:
    - Core benchmark engine
    - Model adapters (Hugging Face, Ollama, API)
    - Task management system
    - Result storage and analysis
  - Pydantic for data validation
  - Structured logging with correlation IDs
  - Async processing for concurrent benchmarks
- **Benchmark Service**: Manages benchmark runs, status tracking, and results analysis.
- **Category Service**: Handles CRUD operations for categories and task assignments.
- **Task Service**: Manages CRUD operations for tasks, category assignments, and status.
- **Template Service**: Handles CRUD operations, validation, and task listing for templates.
- **Model Service**: Manages CRUD operations and testing for AI models.
- **Import/Export Service**: Provides data export/import functionality.

Each service will have its own:
- Routes (API endpoints)
- Schemas (request/response models)
- Services (business logic)
- Repositories (data access)
- Models (Pydantic models)
- Configuration

### Core Components
- Configuration system using Pydantic Settings in `app/config.py`
- Data models defined with Pydantic in `app/models.py` (shared models)
- Enum definitions in `app/enums.py` (shared enums)
- Custom exceptions in `app/exceptions.py` (shared exceptions)
- JSON-based data storage utilities in `app/utils.py`
- Model adapters in `app/adapters/`:
  - `base.py` - Base adapter interface and factory
  - `huggingface.py` - Adapter for Hugging Face models
  - `ollama.py` - Adapter for Ollama models

### Data Management
- JSON-based data store
  - File-based organization by entity type
  - Indexing for efficient querying
  - Versioning for data evolution
  - Transaction-like operations for data integrity
- Efficient read/write patterns
  - Caching frequently accessed data
  - Optimized JSON parsing for large datasets
  - Atomic file operations to prevent corruption

### Frontend Architecture
- Svelte 5 + TypeScript
  - Component library for visualization
  - Task creation and management interface
  - Model configuration panels
  - Real-time benchmark monitoring
  - Responsive design with Tailwind CSS

### Security Considerations
- Secure storage for API credentials
- Input validation and sanitization

### Deployment Options
- Docker containers with compose for easy setup
- Volume mapping for persistent storage
- Environment configuration for different deployment scenarios

## UI Design

### Layout & Navigation

#### Application Layout
- **Three-panel Layout**
  - Left sidebar: Primary navigation and model selection
  - Main content area: Task/category details and benchmark results
  - Right panel: Context-sensitive configuration and details
- **Collapsible panels** for maximizing work area
- **Persistent status bar** showing active model, current operation, and system status

#### Navigation Structure
- **Primary Navigation Areas**:
  - Dashboard (Overview)
  - Categories
  - Tasks
  - Models
  - Templates
  - Results
  - Settings
- **Breadcrumb navigation** for deep hierarchies
- **Recent items** quick access

### Dashboard Design

#### Main Dashboard
- **Hero Section**: Summary metrics of last benchmark run
- **Model Comparison Panel**: Interactive radar chart comparing model performance across categories
- **Quick Actions**: Add/Delete models, categories from view

#### Category Dashboard
- **Performance Overview**: Bar charts showing model/models performance in the category
- **Task Breakdown**: Table showing all tasks in the category with status indicators
- **Filtering Options**: Filter by model or specific metrics

### Benchmark Execution UI

#### Benchmark Configuration
- **Model Selection**: Select interface for models to benchmark
- **Category/Task Selection**: Tree-view selector for tasks/categories
- **Parameter Configuration**: Collapsible panels for setting benchmark parameters

#### Execution Monitoring
- **Progress Indicators**: Per-task and overall progress bars
- **Cancel/Pause Controls**: Ability to manage running benchmarks

### Results Visualization

#### Comparative Views
- **Radar Charts**: For multi-dimension comparison across categories
- **Bar Charts**: For direct model/models performance comparison
- **Tables**: For detailed metric examination


### Category and Task Management Interfaces

#### Category Editor
- **Category Creation**: Form-based interface for creating new categories
- **Task Assignment**: Drag-and-drop interface for assigning tasks to categories
- **Category Details**: Overview of category metrics and tasks
- **Category Export/Import**: For sharing category benchmarks

#### Task Editor
- **Template-based Creation**: Wizard interface for creating tasks from templates
- **Input Configuration**: Form-based interface for configuring task inputs
- **Output Validation**: Preview of expected outputs and validation rules
- **Preview**: Interface for previewing task final state before adding to benchmark
- **Draft**: Save task as draft for later completion

#### Task Listing
- **Sortable/Filterable Table**: For managing large task collections
- **Batch Operations**: For managing multiple tasks
- **Status Indicators**: Visual indicators for task status (draft, ready, error)
- **Task Assignment**: Drag-and-drop interface for assigning tasks to categories
- **Category Details**: Overview of category metrics and tasks
- **Category Export/Import**: For sharing category benchmarks

### Model Management

#### Model Configuration
- **Parameter Editor**: Form-based interface for model parameters
- **Credential Management**: Interface for API keys
- **Resource Allocation**: Controls for memory and compute allocation

### Component Library

#### Design System
- **Typography**:
  - Primary Font: Montserrat
  - Scale: 12px/0.75rem (small), 14px/0.875rem (base), 16px/1rem (large), 20px/1.25rem (xl)

- **Component Variants**:
  - Buttons: Primary, Secondary, Tertiary, Danger
  - Cards: Standard, Interactive, Status
  - Form Controls: Input, Select, Toggle, Slider

#### UI Components
- **Data Tables**: Sortable, filterable, with pagination
- **Charts**: Line, bar, radar, scatter with interactive tooltips
- **Forms**: Standardized input components with validation
- **Modals/Dialogs**: For workflow interruptions and confirmations
- **Toast Notifications**: For system feedback
- **Loading States**: Skeleton loaders, progress indicators

### Interaction Design

#### State Transitions
- **Loading States**: Skeleton screens for initial loads
- **Transitions**: Subtle animations for state changes (300ms easing)
- **Feedback**: Immediate visual feedback for user actions
- **Errors**: Clear error states with recovery actions

#### User Workflows
- **Benchmark Creation**: 3-step wizard (select category → select tasks → configure)
- **Result Analysis**: Hierarchical drill-down (category → task → details)
- **Import/Export**: Step-by-step wizard with preview and validation

### Accessibility Considerations
- **Keyboard Navigation**: Full keyboard support with visible focus states
- **Color Contrast**: WCAG AA compliance for text readability
- **Screen Reader Support**: Semantic HTML and ARIA attributes
- **Focus Management**: Logical tab order and focus trapping in modals

### Responsive Design
- **Responsive Desktop Design**: 
  - Collapsed sidebar on smaller screens
  - Responsive grid for dashboard components
  - Priority content visibility for limited screen real estate

### Design Implementation Approach
- **Component-first Development**: Build and test individual components before full pages
- **Layout Containers**: Flexible grid system for consistent spacing
- **Style Encapsulation**: Scoped styles for components
- **Reusable Patterns**: Extract common patterns into shared components
