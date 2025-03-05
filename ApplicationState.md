# Application State Documentation

## How to work with this document

This document provides a snapshot of the current state of the LocalAI Bench application. 
It is a way of communicating the current state of the application between the AI developer and the Project Manager.
It includes details about the data models, services, API endpoints, and UI components. It also contains information about what should be implemented next and any known issues or bugs - as a guideline for you as a AI developer.
This document is intended to be a living document that is updated as the application evolves - when you make changes to the application, you should update this document to reflect those changes in the 'Current State' section and mark tasks as done in the 'Action Points' section. 
When Project Manager reviews the application, they will refer to this document to understand the current state of the application and add new requirements or changes to the 'Action Points' section.

## Current State
### Project Structure
The project is structured as follows:
- Backend code is located in the `/app` directory
- Frontend code is located in the `/ui` directory

### Backend Components
- Configuration system using Pydantic Settings in `app/config.py`
- Data models defined with Pydantic in `app/models.py`
- Enum definitions in `app/enums.py`
- Custom exceptions in `app/exceptions.py`
- JSON-based data storage utilities in `app/utils.py`
- Data access repositories in `app/repositories.py`
- Core benchmark engine services in `app/services.py`, including:
  - `BenchmarkEngine` for task execution and scoring calculations
  - `BenchmarkService` for managing benchmark runs, status tracking and results analysis
  - `ModelService` for managing AI models
  - `CategoryService` for managing categories
  - `TemplateService` for managing templates
  - `TaskService` for managing tasks
  - `ImportExportService` for data import/export operations
- Model adapters in `app/adapters/`:
  - `base.py` - Base adapter interface and factory
  - `huggingface.py` - Adapter for Hugging Face models
  - `ollama.py` - Adapter for Ollama models
- Directory structure for JSON storage:
  - `/data/categories` - Category data
  - `/data/tasks` - Task data
  - `/data/templates` - Template data
  - `/data/models` - Model configuration data
  - `/data/results` - Benchmark results data
  - `/data/images` - Image storage for UI tasks

### Model Adapters
The application now includes a flexible adapter system for different model types:
- `ModelAdapter` abstract base class defines a common interface for all model adapters
- `ModelAdapterFactory` provides a factory pattern for creating adapters based on model configuration
- Implemented adapters:
  - `HuggingFaceAdapter` supports models from Hugging Face Hub with features like:
    - GPU/CPU selection based on availability and model requirements
    - Support for different quantization options (int8, int4, fp16)
    - Token counting for input text
    - Both streaming and non-streaming generation
  - `OllamaAdapter` integrates with Ollama API, providing:
    - Automatic model pulling if not available locally
    - Parameter mapping between internal representation and Ollama API
    - Token counting via Ollama API
    - Both streaming and non-streaming generation

### Core Benchmark Engine
The benchmark engine implementation now provides:
- Asynchronous execution of benchmarks against multiple models
- Task execution with proper error handling and resource management
- Score calculation using the configurable weights formula from ProjectPlan.md
- Comprehensive reporting with detailed breakdowns of performance metrics
- Status tracking for benchmark runs with progress monitoring
- Support for cancelling running benchmarks

### Core Backend API
The FastAPI application has been set up with:
- Main application setup in `app/main.py` with:
  - CORS middleware configuration
  - Static files serving
  - Custom exception handlers for all application exceptions
  - Directory structure initialization on startup
  - Basic health check endpoints (/ and /status)
  - Mounted routers for all API endpoints
  - Structured logging integration

### API Routes
All API routes have been implemented in `app/routes.py` with comprehensive endpoint groups:
- Category management (/api/categories/):
  - CRUD operations for categories
  - Task assignment management
- Template management (/api/templates/):
  - CRUD operations for templates
  - Template validation
  - Task listing by template
- Task management (/api/tasks/):
  - CRUD operations for tasks
  - Category assignment
  - Status management
- Model management (/api/models/):
  - CRUD operations for models
  - Model testing functionality
- Benchmark management (/api/benchmarks/):
  - Benchmark creation and execution
  - Status monitoring
  - Results retrieval
- Import/Export functionality (/api/import-export/):
  - Data export by type
  - Import preview with conflict detection
  - Data import with referential integrity checks

## Action Points (What should be implemented next)

### Initial Project Setup
- [x] Create a project structure
- [x] Create config.py with application settings and environment variables
- [ ] Set up Docker configuration for development environment

### Data Models
- [x] Create models.py with Pydantic models for:
  - [x] Category
  - [x] Task
  - [x] Template
  - [x] Model
  - [x] BenchmarkResult
- [x] Create enums.py with Enums for:
  - [x] TaskStatus
  - [x] TemplateType
  - [x] EvaluationCriteriaType
  - [x] ModelType

### Data Storage
- [x] Implement JSON-based data storage utilities in utils.py
- [x] Create repositories.py with data access functions
- [x] Set up file organization structure as defined in project plan
- [x] Implement versioning for data files

### Core Backend Services
- [x] Create services.py with core benchmark engine logic
- [x] Implement model adapters for Hugging Face integration
- [x] Implement model adapters for Ollama integration
- [ ] Implement model adapters for API providers
- [ ] Create task management system with template support
- [x] Implement scoring calculation with configurable weights

### API Endpoints
- [x] Set up FastAPI in main.py
- [x] Create schemas.py for request/response models
- [x] Implement structure in routes.py with endpoints for:
  - [x] Category management
  - [x] Task management
  - [x] Template management
  - [x] Model configuration
  - [x] Benchmark execution
  - [x] Results retrieval
- [x] Implement routes functionalities
- [ ] Add request validation middleware
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Set up API documentation with examples

### Frontend Structure
- [x] Set up Svelte 5 project with TypeScript
- [ ] Configure Tailwind CSS
- [ ] Create component library based on UI design specs
- [ ] Implement three-panel layout structure

### UI Components
- [ ] Develop dashboard with overview metrics
- [ ] Create category management interface
- [ ] Implement task editor with template support
- [ ] Build model configuration panels
- [ ] Design results visualization components with charts
- [ ] Implement benchmark execution UI with progress indicators

### Import/Export Functionality
- [x] Create export utilities for benchmark suites, categories, tasks, and results
- [x] Implement import process with validation and conflict resolution
- [ ] Add UI for export/import workflows

### Testing
- [ ] Set up unit testing for backend services
- [ ] Create integration tests for API endpoints
- [ ] Implement frontend component tests
- [ ] Design sample benchmarks for system testing

### Documentation
- [ ] Document API endpoints
- [ ] Create user guide for benchmark creation
- [ ] Prepare developer documentation

### Deployment
- [ ] Configure Docker compose for production deployment
- [ ] Set up volume mapping for persistent storage
- [ ] Create environment configuration templates



