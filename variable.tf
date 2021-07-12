variable "region" {
  default = "ap-northeast-2"
}

variable "schedule" {
  default = "cron(0 0 * */2 ? *))"
}