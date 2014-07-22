from automaton import api as ctool
from automaton.cluster import get_cluster_names, get_cluster

#launch 6 node cluster via ctool (5 for nodes, 1 test coordinator)

clusterName = 'cassa72'
numNodes = '6'
platform = 'ubuntu'

ctool.Cluster().launch(clusterName, numNodes, platform)
cluster = ctool.Cluster().get_cluster(clusterName)

#configure some properties to allow easier ssh
script = [
    "sudo sed -i 's/node/n/g' /etc/hosts",
    "echo "" >> /home/automaton/.ssh/config",
    "echo 'Host n*' >> /home/automaton/.ssh/config",
    "echo 'IdentityFile /home/automaton/.ssh/automaton_id_rsa' >> /home/automaton/.ssh/config",
    "echo 'StrictHostKeyChecking=no' >> /home/automaton/.ssh/config"
]

script = "\n".join(script)
ctool.Cluster().run(clusterName, 'all', script, stream=False, format_results=True)

# get and install modified/preconfigured jepsen and dependencies
script = [
    "wget 'https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein'",
    "sudo mv lein /bin/lein",
    "chmod a+x /bin/lein",
    "lein",
    "git clone https://github.com/shawnkumar/cassa72.git",
    "lein deps"
]

script = "\n".join(script)
ctool.Cluster().run(clusterName, '0', script, stream=False, format_results=True)

#set up test configuration and start cassandra on test nodes
script = [
    "\curl -sSL https://get.rvm.io | bash -s stable",
    "source /home/automaton/.rvm/scripts/rvm",
    "rvm install ruby 1.9.3",
    "rvm use 1.9.3",
    "gem install salticid",
    "touch ~/.salticidrc",
    "echo 'load ENV[=HOME=] + =/cassa72/salticid/*.rb=' >> ~/.salticidrc", #find non-hacky quote fix
    "sudo sed -i 's/=/\"/g' ~/.salticidrc",
    "salticid base.setup",
    "salticid cassandra.setup",
    "salticid cassandra.start"
]

script = "\n".join(script)
ctool.Cluster().run(clusterName, '0', script, stream=False, format_results=True)
