#
# vagrantfile to build opencv vm for development
#

$script = <<SCRIPT
export ANSIBLE_FORCE_COLOR=1

# boostrap ansible install

# install pip if required
if [ ! -x "/usr/local/bin/pip" ];
then
    sudo apt-get update -qq
    sudo apt-get install -y python-dev autoconf g++
    wget https://bootstrap.pypa.io/get-pip.py -O get-pip.py
    sudo python get-pip.py
fi
# install ansible if required
if [ $(pip freeze | grep -c ansible) -eq 0 ];
then
    echo "installing ansible for provisioning"
    export DEBIAN_FRONTEND=noninteractive
    sudo pip install -q ansible
fi

# provision
cd /vagrant/ansible
ansible-playbook ./setup.yml -i 'localhost,' --connection=local
SCRIPT

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

    ENV['VAGRANT_DEFAULT_PROVIDER'] = 'docker'

    # build ingest machine
    config.vm.hostname = "anello"
    config.vm.provider :docker do |d|
        d.build_dir = "."
        d.has_ssh = true
        d.name = "dello"
        d.build_args = ["-t", "anello:1"]
        d.ports = [ "8000:8000"]
    end

    #config.vm.network :forwarded_port, guest: 8000, host: 8000

    config.ssh.port = 22

    # install ansible and provision
    config.vm.provision :shell, inline: $script

end