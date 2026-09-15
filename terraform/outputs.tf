output "ecr_repository_url" {
  description = "Push the application image to this ECR repository."
  value       = aws_ecr_repository.app.repository_url
}

output "service_url" {
  description = "Public URL of the RAG Workbench service."
  value       = "https://${aws_apprunner_service.app.service_url}"
}
