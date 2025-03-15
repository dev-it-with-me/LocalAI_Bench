import type { 
  TaskResponse, 
  TaskCreateRequest, 
  TaskUpdateRequest, 
  Category,
  ModelResponse,
  ModelCreateRequest,
  ModelUpdateRequest
} from './type';

// Base API URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// Default fetch options for all requests
const fetchOptions: RequestInit = {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  }
};

// Model operations
async function getModels(): Promise<ModelResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/models`, fetchOptions);
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to fetch models');
  }
  const data = await response.json();
  return data.models || [];
}

async function createModel(modelData: ModelCreateRequest): Promise<ModelResponse> {
  const response = await fetch(`${API_BASE_URL}/api/models`, {
    ...fetchOptions,
    method: 'POST',
    body: JSON.stringify(modelData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create model');
  }
  
  return await response.json();
}

async function updateModel(id: string, modelData: ModelUpdateRequest): Promise<ModelResponse> {
  const response = await fetch(`${API_BASE_URL}/api/models/${id}`, {
    ...fetchOptions,
    method: 'PATCH',
    body: JSON.stringify(modelData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update model');
  }
  
  return await response.json();
}

async function deleteModel(id: string): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/models/${id}`, {
    ...fetchOptions,
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete model');
  }
  
  return true;
}

async function getCategories(): Promise<Category[]> {
  const response = await fetch(`${API_BASE_URL}/api/categories`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  return data.categories || [];
}

async function getCategory(id: string): Promise<Category> {
  const response = await fetch(`${API_BASE_URL}/api/categories/${id}`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

async function createCategory(categoryData: {
  name: string;
  description: string;
}): Promise<Category> {
  const response = await fetch(`${API_BASE_URL}/api/categories`, {
    ...fetchOptions,
    method: 'POST',
    body: JSON.stringify(categoryData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create category');
  }
  
  return await response.json();
}

async function updateCategory(id: string, categoryData: {
  name?: string;
  description?: string;
}): Promise<Category> {
  const response = await fetch(`${API_BASE_URL}/api/categories/${id}`, {
    ...fetchOptions,
    method: 'PATCH',
    body: JSON.stringify(categoryData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update category');
  }
  
  return await response.json();
}

async function deleteCategory(id: string): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/categories/${id}`, {
    ...fetchOptions,
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete category');
  }
  
  return true;
}

async function getTasks(): Promise<TaskResponse[]> {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  return Array.isArray(data) ? data : data.tasks || [];
}

async function getTask(id: string): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

async function createTask(taskData: TaskCreateRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, {
    ...fetchOptions,
    method: 'POST',
    body: JSON.stringify(taskData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to create task');
  }
  
  return await response.json();
}

async function updateTask(id: string, taskData: TaskUpdateRequest): Promise<TaskResponse> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    ...fetchOptions,
    method: 'PATCH',
    body: JSON.stringify(taskData)
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to update task');
  }
  
  return await response.json();
}

async function deleteTask(id: string): Promise<boolean> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, {
    ...fetchOptions,
    method: 'DELETE'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete task');
  }
  
  return true;
}

async function getBenchmarks(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/benchmarks`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

export { 
  getModels,
  createModel,
  updateModel,
  deleteModel,
  getCategories, 
  getCategory,
  createCategory,
  updateCategory,
  deleteCategory,
  getTasks, 
  getTask,
  createTask,
  updateTask,
  deleteTask,
  getBenchmarks
};