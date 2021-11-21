resource "digitalocean_droplet" "machinetwo" {
  image = "ubuntu-16-04-x64"
  name = "machinetwo"
  region = "fra1"
  size = "s-1vcpu-1gb"
  private_networking = true
  ssh_keys = [
    "${var.ssh_fingerprint}"
  ]
  connection {
    user = "root"
    type = "ssh"
    private_key = file("${var.pvt_key}")
    timeout = "2m"
    host = digitalocean_droplet.machinetwo.ipv4_address
  }
  provisioner "remote-exec" {
      inline = [
          # "apt-get --assume-yes update",
          # "apt-get --assume-yes upgrade", 

          "curl -sSL https://get.docker.com/ | sh",
          "apt-get --assume-yes install docker-compose",

          # clone project using gitlab deploy token
          "git clone --single-branch --branch develop http://gitlab+deploy-token-22:xA2kXszy-U5343JJe4sE@gitlab.beuth-hochschule.de/s76441/chk_devops_ws19.git",
          "cd chk_devops_ws19",

          # set current ip
          "ip=$(curl -4 ifconfig.co)",
          "echo 'VUE_APP_API_URL='http://$ip:'' > ./app/frontend/.env",  

          "echo 'VUE_APP_API_PORT='5000'' >> ./app/frontend/.env",

          # use develop-compose file for configuration
          "docker-compose -f ./app/develop-compose.yml build",
          "docker-compose -f ./app/develop-compose.yml up -d",
          
          # Old approach via quay.io
          # "docker pull quay.io/chkissel/devops_ws19:server",
          # "docker pull quay.io/chkissel/devops_ws19:frontend",
          # "docker run --name server_test -d -p 5000:5000 quay.io/chkissel/devops_ws19:server",
          # "docker run -d -p 80:8080 --name frontend_test quay.io/chkissel/devops_ws19:frontend"
      ]
  }
}