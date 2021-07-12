terraform {
  required_version = ">=0.13"

  required_providers {
    aws = {
      version = ">=2.70.0"
    }
  }
}

provider "aws" {
  region  = var.region
}