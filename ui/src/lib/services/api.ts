// Base API URL
const API_BASE_URL = 'http://127.0.0.1:8000';

// Default fetch options for all requests
const fetchOptions: RequestInit = {
  credentials: 'include',
  headers: {
    'Content-Type': 'application/json',
  }
};

async function getModels(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/models`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

async function getCategories(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/categories`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  return data.categories || [];
}

async function getCategory(id: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/categories/${id}`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

async function createCategory(categoryData: {
  name: string;
  description: string;
}): Promise<any> {
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
}): Promise<any> {
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

async function getTasks(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/tasks`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  const data = await response.json();
  return data.tasks;
}

async function getTask(id: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/tasks/${id}`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

async function createTask(taskData: {
  name: string;
  description: string;
  category_id: string;
  template_id: string;
  input_data: Record<string, any>;
  expected_output: Record<string, any>;
  complexity: number;
  accuracy_weight: number;
  latency_weight: number;
  throughput_weight: number;
  cost_weight: number;
}): Promise<any> {
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

async function updateTask(id: string, taskData: {
  name?: string;
  description?: string;
  category_id?: string;
  template_id?: string;
  input_data?: Record<string, any>;
  expected_output?: Record<string, any>;
  complexity?: number;
  accuracy_weight?: number;
  latency_weight?: number;
  throughput_weight?: number;
  cost_weight?: number;
}): Promise<any> {
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

async function getTemplates(): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/api/templates`, fetchOptions);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return await response.json();
}

export { 
  getModels, 
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
  getBenchmarks, 
  getTemplates 
};