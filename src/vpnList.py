import subprocess
import alp
import sys
import re

class Options(object):
    CASE_INSENSITIVE = "-i"

def run_bash_command(command):
    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    return proc.stdout.read().splitlines()

def parse_input(strn):
    if (strn):
        args = strn.split(" ")
        options = args[:-1]
        search_string = args[-1]
        return (options, search_string)
    return ([],"")

def get_networks_list():
    network_list_command = "networksetup -listallnetworkservices" 
    return run_bash_command(network_list_command)
    
def find_VPNs(networks_list, grep_string, options):
    flags = 0
    flags |= re.IGNORECASE if Options.CASE_INSENSITIVE in options else 0
    vpnFilter = lambda strn : bool(re.search(grep_string, strn, flags))
    return filter(vpnFilter, networks_list)

def get_connected_network_interfaces():
    list_network_interfaces = "scutil --nc list"
    network_interfaces = run_bash_command(list_network_interfaces)
    is_connected = lambda connection : bool(re.search("[^a-zA-Z]Connected", connection, re.IGNORECASE))
    def extract_connection_name(connection):
        match = re.search("\".*\"", connection)
        if (match):
            return match.group().replace("\"", "")
        return ""
    return dict((extract_connection_name(connection),is_connected(connection)) for connection in network_interfaces)

def check_VPN_connected(vpn_name):
    return get_connected_network_interfaces().get(vpn_name, False)


def get_icon(vpn_name):
    return "connected.png" if check_VPN_connected(vpn_name) else "disconnected.png"

if __name__ == "__main__":
    grep_string = "vpn"
    options = [Options.CASE_INSENSITIVE]
    try:
    	options, grep_string = parse_input(sys.argv[1])
    except Exception, e:
    	pass
    
    networks_list = get_networks_list()
    vpnList = find_VPNs(networks_list, grep_string, options)
    
    vpns = [alp.Item(arg=vpn, title=vpn, icon=get_icon(vpn)) for vpn in vpnList]
    print alp.feedback(vpns)