variable "aws_region" {
  description = "AWS region for the service."
  type        = string
  default     = "us-east-1"
}

variable "service_name" {
  description = "App Runner service name."
  type        = string
  default     = "rag-workbench"
}

variable "image_tag" {
  description = "Container tag already pushed to ECR."
  type        = string
  default     = "latest"
}

variable "llm_base_url" {
  description = "Optional OpenAI-compatible LLM endpoint."
  type        = string
  default     = ""
}

variable "llm_model" {
  description = "Optional model name for the LLM endpoint."
  type        = string
  default     = "local-model"
}
