from plugin.globals import *
from plugin.network_manager import *


# ################ CREAZIONE RETE DI PROGETTO

network, subnet = manage_network()

network_ext = pstack.networking.get_network(name=config.require("external_net"))


