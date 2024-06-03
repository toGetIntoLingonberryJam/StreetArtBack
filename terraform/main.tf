# Настраиваем провайдер Yandex Cloud
terraform {
  required_providers {
    yandex = {
      source  = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

# Конфигурация  провайдера Yandex Cloud
provider "yandex" {
  service_account_key_file = "key.json"
  cloud_id                = var.cloud_id
  folder_id               = var.folder_id
  zone                    = var.zone
}

# ==============================
# 1. Создание S3 бакета
# ==============================
resource "yandex_storage_bucket" "bucket" {
  bucket = var.bucket_name
  folder_id = var.folder_id 
  access_key = data.yandex_lockbox_secret_version.secret_sa_key.entries[0].text_value
  secret_key = data.yandex_lockbox_secret_version.secret_sa_key.entries[1].text_value
  acl    = "public-read"  
}

# ==============================
# 2. Создание Сетей/Подсетей
# ==============================
resource "yandex_vpc_network" "network-1" {
  name = "from-terraform-network"
}

resource "yandex_vpc_subnet" "subnet-1" {
  name           = "from-terraform-subnet"
  zone           = "ru-central1-a"
  network_id     = "${yandex_vpc_network.network-1.id}"
  v4_cidr_blocks = ["10.5.0.0/24"]
}


# ==============================
# 3. Создание сервиса PostgreSQL
# ==============================
resource "yandex_mdb_postgresql_cluster" "postgres-clu" {
  name        = "postgres-clu"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.network-1.id
  security_group_ids  = [yandex_vpc_security_group.db_access.id]
  
  config {
    version        = "15"
    resources {
      resource_preset_id = "s2.micro"
      disk_size         = 16
      disk_type_id      = "network-ssd"
    }
    postgresql_config = {
      max_connections                   = 395
      enable_parallel_hash              = true
      vacuum_cleanup_index_scale_factor = 0.2
      autovacuum_vacuum_scale_factor    = 0.34
      default_transaction_isolation     = "TRANSACTION_ISOLATION_READ_COMMITTED"
      shared_preload_libraries          = "SHARED_PRELOAD_LIBRARIES_AUTO_EXPLAIN,SHARED_PRELOAD_LIBRARIES_PG_HINT_PLAN"
    }
  }

  host {
    zone      = "ru-central1-a"
    subnet_id = yandex_vpc_subnet.subnet-1.id
  }
  
  depends_on  = [yandex_vpc_network.network-1, yandex_vpc_subnet.subnet-1]
}  

resource "yandex_mdb_postgresql_database" "db" {
  cluster_id = yandex_mdb_postgresql_cluster.postgres-clu.id
  name       = var.db_name
  owner      = var.db_user
  depends_on = [
    yandex_mdb_postgresql_user.user
  ]
}

resource "yandex_mdb_postgresql_user" "user" {
  cluster_id = yandex_mdb_postgresql_cluster.postgres-clu.id
  name       = var.db_user
  password   = var.db_pass
}

# ==============================
# 4. Создание сервиса Redis
# ==============================
resource "yandex_mdb_redis_cluster" "redis" {
  name        = "street-art-redis"
  environment = "PRESTABLE"
  network_id  = yandex_vpc_network.network-1.id
  security_group_ids  = [yandex_vpc_security_group.db_access.id]
  
  
  config {
    password = var.redis_pass
    version = "6.2"
  }
  
  resources {
    resource_preset_id = "b3-c1-m4"
    disk_size = 16
  }

  host {
    zone      = "ru-central1-a"
    subnet_id = yandex_vpc_subnet.subnet-1.id
  }
  
  depends_on  = [yandex_vpc_network.network-1, yandex_vpc_subnet.subnet-1]
}

# ==============================
# 5. Создание Security Group
# ==============================
resource "yandex_vpc_security_group" "web_sg" {
  name                = "web-sg"
  network_id  = "${yandex_vpc_network.network-1.id}" 
  description = "Доступ на HTTP/HTTPs + SSH"
  
  ingress {
    description       = "Allow HTTPS"
    protocol          = "TCP"
    port              = 443
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }

  ingress {
    description       = "Allow HTTP"
    protocol          = "TCP"
    port              = 80
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }

  ingress {
    description       = "Allow SSH"
    protocol          = "TCP"
    port              = 22
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }
  
  egress {
    description       = "Permit ANY"
    protocol          = "ANY"
    v4_cidr_blocks    = ["0.0.0.0/0"]
  }
}
resource "yandex_vpc_security_group" "db_access" {
  name        = "street-art-db-access"
  network_id  = "${yandex_vpc_network.network-1.id}" 
  description = "Allow access to PostgreSQL and Redis from VM"
  
  # Ниже правила для разрешения подключения с любых адресов подсети
  # Правило для PostgreSQL
  ingress {
    description    = "Allow PostgreSQL access"
    port           = 6432
    protocol       = "TCP"
    security_group_id = yandex_vpc_security_group.web_sg.id
    v4_cidr_blocks = ["10.5.0.0/24"]
  }

  # Правило для Redis
  ingress {
    description    = "Allow Redis access"
    port           = var.redis_port
    protocol       = "TCP"
    security_group_id = yandex_vpc_security_group.web_sg.id
    v4_cidr_blocks = ["10.5.0.0/24"]
  }
  
}

# ==============================
# 6. Создание виртуальной машины
# ==============================
data "yandex_compute_image" "last_ubuntu" {
  family = "ubuntu-2204-lts"  # ОС (Ubuntu, 22.04 LTS)
}

resource "yandex_compute_instance" "vm" {
  depends_on = [yandex_mdb_postgresql_database.db, yandex_mdb_redis_cluster.redis]

  name = "street-art-back"
  platform_id = "standard-v3"
  zone = var.zone
  allow_stopping_for_update = true
  
  resources {
    core_fraction = 20 # Гарантированная доля vCPU
    cores  = 2
    memory = 2
  }
  
  boot_disk {
    initialize_params {
      image_id = data.yandex_compute_image.last_ubuntu.id  # ID образа Ubuntu
    }
  }
  network_interface {
    subnet_id = yandex_vpc_subnet.subnet-1.id
    nat = true  # Для выдачи машине внешнего IP-адреса
    security_group_ids = [yandex_vpc_security_group.web_sg.id] 
  }


  metadata = {
    user-data = "${templatefile("./meta.yml", {
      username = var.vm_user, 
      ssh_key = file(var.path_to_ssh_public)  # Читаем ключ из файла 
    })}"
  }
  
  connection {
    type        = "ssh"
    user        = var.vm_user
    private_key = file(var.path_to_ssh_private) 
    host        = self.network_interface.0.nat_ip_address
  }


  # Генерация файла .env
  provisioner "local-exec" {
    command = <<-EOF
      cat <<EOFF > generated.env
MODE=${var.mode}
REDIS_URL=redis://:${var.redis_pass}@${yandex_mdb_redis_cluster.redis.host.0.fqdn}:${var.redis_port}
POSTGRES_HOST=${yandex_mdb_postgresql_cluster.postgres-clu.host.0.fqdn}
POSTGRES_PORT=6432
POSTGRES_DB=${yandex_mdb_postgresql_database.db.name}
POSTGRES_USER=${yandex_mdb_postgresql_user.user.name}
POSTGRES_PASSWORD=${yandex_mdb_postgresql_user.user.password}
POSTGRES_SSL_MODE=verify-full
SECRET_KEY_JWT=${data.yandex_lockbox_secret_version.secret_jwt.entries[0].text_value}
SECRET_VERIFICATION_TOKEN=${data.yandex_lockbox_secret_version.secret_jwt.entries[1].text_value}
SECRET_RESET_TOKEN=${data.yandex_lockbox_secret_version.secret_jwt.entries[2].text_value}
BACKEND_URL=http://${self.network_interface.0.nat_ip_address}
QUEUE_URL=${var.queue_url}
AWS_ACCESS_KEY_ID=${data.yandex_lockbox_secret_version.secret_sa_key.entries[0].text_value}
AWS_SECRET_ACCESS_KEY=${data.yandex_lockbox_secret_version.secret_sa_key.entries[1].text_value}
BUCKET_NAME=${yandex_storage_bucket.bucket.bucket}
EOFF
EOF
  }

  provisioner "file" {
    source  = "generated.env"  # local public key
    destination  = "/tmp/.env"  # will copy to remote VM as /tmp/test.pub
  }

  # Установка Docker, сертификата PostgreSQL и зависимостей
  provisioner "remote-exec" {
    inline = [
      "sudo apt update",

      "sudo curl -s -o - https://get.docker.com | bash -",
      "sudo systemctl enable docker",
      "sudo systemctl start docker",

      # Создаём директорию для секретов
      "sudo mkdir -p /etc/secrets",
      "sudo chmod 777 /etc/secrets",

      "sudo mv /tmp/.env /etc/secrets/",
      
      "git clone https://github.com/toGetIntoLingonberryJam/StreetArtBack --branch ya-cloud /home/${var.vm_user}/StreetArtBack",
      "cd /home/${var.vm_user}/StreetArtBack && sudo docker compose up -d"

    ]
  }
}

# ==============================
#  Получение данных из Lockbox
# ==============================
data "yandex_lockbox_secret_version" "secret_sa_key" {
  secret_id = var.secret_id_sa_key
}

data "yandex_lockbox_secret_version" "secret_jwt" {
  secret_id = var.secret_id_jwt
}

# ==============================
#  Вывод данных
# ==============================
output "external_ip_address_vm_1" {
  value = yandex_compute_instance.vm.network_interface.0.nat_ip_address
}
