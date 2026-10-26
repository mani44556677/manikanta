resource "azurerm_resource_group" "demo" {
  name     = "rg-manikanta-showcase"
  location = var.location
  tags = {
    project     = "devops-showcase"
    environment = "demo"
  }
}

# Basic ACR is a paid demo registry. AKS is intentionally a later milestone.
resource "azurerm_container_registry" "demo" {
  name                = var.registry_name
  resource_group_name = azurerm_resource_group.demo.name
  location            = azurerm_resource_group.demo.location
  sku                 = "Basic"
  admin_enabled       = false
  tags                = azurerm_resource_group.demo.tags
}
