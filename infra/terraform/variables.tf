variable "subscription_id" {
  type        = string
  description = "Azure subscription used for this isolated demo."
}

variable "location" {
  type    = string
  default = "eastus"
}

variable "registry_name" {
  type        = string
  description = "Globally unique ACR name: 5-50 lowercase letters and digits."
  validation {
    condition     = can(regex("^[a-z0-9]{5,50}$", var.registry_name))
    error_message = "Use 5-50 lowercase letters and digits."
  }
}
