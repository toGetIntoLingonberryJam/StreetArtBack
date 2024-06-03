# Объявляем переменные: название и тип данных (значения будут подставляться из указанного .tfvars файла)
#=========== main ==============

variable "vm_user" {
  type = string
}

variable "path_to_ssh_public" {
  type = string
  default = "~/.ssh/id_rsa.pub" # Путь к файлу с публичным ключом
}
variable "path_to_ssh_private" {
  type = string
  default = "~/.ssh/id_rsa" # Путь к файлу с приватным ключом
}

variable "cloud_id" {
  description = "ID облака Yandex Cloud"
  type        = string
}
variable "folder_id" {
  description = "ID каталога Yandex Cloud"
  type        = string
}
variable "zone" {
  description = "Зона доступности"
  type        = string
  default     = "ru-cenral1-a"
}

variable "bucket_name" {
  type = string
}

variable "db_name" {
  type = string
}
variable "db_user" {
  type = string
}
variable "db_pass" {
  type = string
}

variable "redis_port" {
  type = string
}
variable "redis_pass" {
  type = string
}

variable "mode" {
  type        = string
  description = "'режим' развёртывания приложения"
  default     = "PROD"
}

variable "secret_id_sa_key" {
  type = string
}
variable "secret_id_jwt" {
  type = string
}
