/**
 * Type definitions for the LocalAI Bench application
 */

/**
 * Task Status Enum
 */
export enum TaskStatusEnum {
  DRAFT = "draft",
  READY = "ready",
  ARCHIVED = "archived",
}


/**
 * Image Input Data
 */
export type ImageInputData = {
  id: string;
  filename: string;
  filepath: string;
}

/**
 * Input Data
 */
export type InputData = {
  user_instruction: string;
  system_prompt: string | null;
  image: ImageInputData[] | null;
}

/**
 * Evaluation Weights
 */
export type EvaluationWeights = {
  complexity: number;
  accuracy: number;
  latency: number;
  cost_memory_usage: number;
}

/**
 * Task Create Request
 */
export type TaskCreateRequest = {
  name: string;
  description?: string;
  category_id?: string | null;
  input_data?: {
    user_instruction: string;
    system_prompt?: string | null;
    image?: ImageInputData[] | null;
  } | null;
  expected_output?: string | null;
  evaluation_weights?: {
    complexity?: number;
    accuracy?: number;
    latency?: number;
    cost_memory_usage?: number;
  } | null;
  status?: TaskStatusEnum;
}

/**
 * Task Update Request
 */
export type TaskUpdateRequest = {
  name?: string | null;
  description?: string | null;
  category_id?: string | null;
  input_data?: {
    user_instruction?: string;
    system_prompt?: string | null;
    image?: ImageInputData[] | null;
  } | null;
  expected_output?: string | null;
  evaluation_weights?: {
    complexity?: number;
    accuracy?: number;
    latency?: number;
    cost_memory_usage?: number;
  } | null;
  status?: TaskStatusEnum | null;
}

/**
 * Task Response
 */
export type TaskResponse = {
  id: string;
  name: string;
  description: string;
  category_id: string;
  status: TaskStatusEnum;
  input_data: InputData;
  expected_output: string | null;
  evaluation_weights: EvaluationWeights | null;
  created_at: string;
  updated_at: string;
}

/**
 * Category
 */
export type Category = {
  id: string;
  name: string;
  description: string;
  task_ids: string[];
  created_at: string;
  updated_at: string;
}
