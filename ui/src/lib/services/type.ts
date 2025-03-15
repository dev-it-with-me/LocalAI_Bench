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

/**
 * Category Create Request
 */
export type CategoryCreateRequest = {
  name: string;
  description?: string;
}

/**
 * Category Update Request
 */
export type CategoryUpdateRequest = {
  name?: string;
  description?: string;
}

/**
 * Category Response Model
 */
export type CategoryModel = {
  id: string;
  name: string;
  description: string;
  task_ids: string[];
  created_at: string;
  updated_at: string;
}

/**
 * Model Provider Enum
 */
export enum ModelProviderEnum {
  HUGGINGFACE = 'HUGGINGFACE',
  OLLAMA = 'OLLAMA',
  CUSTOM_API = 'CUSTOM_API'
}

/**
 * Base Model Configuration
 */
export type BaseModelConfig = {
  model_id: string;
}

/**
 * Ollama Model Configuration
 */
export type OllamaModelConfig = BaseModelConfig & {
  host: string;
  temperature: number;
  top_p: number;
  top_k: number;
  max_tokens: number;
  stop_sequences: string[];
}

/**
 * HuggingFace Model Configuration
 */
export type HuggingFaceModelConfig = BaseModelConfig & {
  use_gpu: boolean;
  max_length: number;
  temperature: number;
}

/**
 * Custom API Model Configuration
 */
export type CustomApiModelConfig = BaseModelConfig & {
  endpoint: string;
  headers: Record<string, string>;
  prompt_key: string;
  response_key: string;
}

/**
 * Model Configuration
 */
export type ModelConfig = 
  | { provider: ModelProviderEnum.OLLAMA; config: OllamaModelConfig }
  | { provider: ModelProviderEnum.HUGGINGFACE; config: HuggingFaceModelConfig }
  | { provider: ModelProviderEnum.CUSTOM_API; config: CustomApiModelConfig };

/**
 * Model Response
 */
export type ModelResponse = {
  id: string;
  name: string;
  description: string;
  provider: ModelProviderEnum;
  config: OllamaModelConfig | HuggingFaceModelConfig | CustomApiModelConfig;
  created_at: string;
  updated_at: string;
}

/**
 * Model Create Request
 */
export type ModelCreateRequest = {
  name: string;
  description?: string;
  provider: ModelProviderEnum;
  config: OllamaModelConfig | HuggingFaceModelConfig | CustomApiModelConfig;
}

/**
 * Model Update Request
 */
export type ModelUpdateRequest = {
  name?: string;
  description?: string;
  config?: OllamaModelConfig | HuggingFaceModelConfig | CustomApiModelConfig;
}
