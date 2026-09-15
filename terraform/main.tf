resource "aws_ecr_repository" "app" {
  name                 = var.service_name
  image_tag_mutability = "MUTABLE"

  image_scanning_configuration {
    scan_on_push = true
  }
}

resource "aws_iam_role" "apprunner_ecr_access" {
  name = "${var.service_name}-ecr-access"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "build.apprunner.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "apprunner_ecr_access" {
  role       = aws_iam_role.apprunner_ecr_access.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSAppRunnerServicePolicyForECRAccess"
}

resource "aws_apprunner_service" "app" {
  service_name = var.service_name

  auto_scaling_configuration_arn = aws_apprunner_auto_scaling_configuration.app.arn

  source_configuration {
    auto_deployments_enabled = false

    authentication_configuration {
      access_role_arn = aws_iam_role.apprunner_ecr_access.arn
    }

    image_repository {
      image_identifier      = "${aws_ecr_repository.app.repository_url}:${var.image_tag}"
      image_repository_type = "ECR"

      image_configuration {
        port                          = "8000"
        runtime_environment_variables = {
          LLM_BASE_URL = var.llm_base_url
          LLM_MODEL    = var.llm_model
        }
        start_command = "uvicorn rag_workbench.api:app --host 0.0.0.0 --port 8000"
      }
    }
  }

  health_check_configuration {
    healthy_threshold   = 2
    unhealthy_threshold = 5
    interval            = 10
    protocol            = "HTTP"
    path                = "/health"
    timeout             = 5
  }

  instance_configuration {
    cpu    = "1 vCPU"
    memory = "2 GB"
  }

  depends_on = [aws_iam_role_policy_attachment.apprunner_ecr_access]
}

resource "aws_apprunner_auto_scaling_configuration" "app" {
  auto_scaling_configuration_name = "${var.service_name}-scaling"
  max_concurrency                 = 50
  max_size                        = 2
  min_size                        = 1
}
