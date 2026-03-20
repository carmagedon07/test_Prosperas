variable "aws_region" {
  description = "Región AWS donde se despliegan los recursos"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Prefijo usado en todos los recursos AWS"
  type        = string
  default     = "prosperas"
}

variable "image_tag" {
  description = "Tag de la imagen Docker a desplegar (ej: latest, sha-abc123)"
  type        = string
  default     = "latest"
}

variable "jwt_secret" {
  description = "Clave secreta para firmar tokens JWT. Almacenada en SSM Parameter Store."
  type        = string
  sensitive   = true
}

variable "jwt_expiry_minutes" {
  description = "Tiempo de expiración del token JWT en minutos"
  type        = number
  default     = 60
}
