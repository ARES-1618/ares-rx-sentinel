#!/usr/bin/env bash
# ==============================================================================
# Project: ARES-RX Sentinel — Milestone M6-B Isolated Security Lab
# Module:  setup_isolated_namespace.sh
# Purpose: Configure isolated Linux network namespaces with virtual ethernet bridge
#          and traffic control (tc) emulating physical RF link delay and jitter.
# Authority: Technical Architect / Research Direction
# ==============================================================================

set -euo pipefail

echo "=== Initializing ARES M6-B Isolated Network Lab ==="

# Check root privileges
if [ "$EUID" -ne 0 ]; then
  echo "[-] Error: Please execute as root (sudo setup_isolated_namespace.sh)"
  exit 1
fi

# Clean existing namespaces if present
ip netns del ns_attacker 2>/dev/null || true
ip netns del ns_receiver 2>/dev/null || true
ip link del br_ares 2>/dev/null || true

# 1. Create Network Namespaces
echo "[+] Creating namespaces: ns_attacker & ns_receiver..."
ip netns add ns_attacker
ip netns add ns_receiver

# 2. Create Virtual Ethernet Bridge
echo "[+] Creating bridge br_ares..."
ip link add name br_ares type bridge
ip link set br_ares up

# 3. Create veth pairs
echo "[+] Creating veth pairs..."
ip link add veth_atk type veth peer name veth_atk_br
ip link add veth_rx type veth peer name veth_rx_br

# 4. Attach bridge ends
ip link set veth_atk_br master br_ares
ip link set veth_rx_br master br_ares
ip link set veth_atk_br up
ip link set veth_rx_br up

# 5. Move endpoint interfaces into respective namespaces
ip link set veth_atk netns ns_attacker
ip link set veth_rx netns ns_receiver

# 6. Configure IP Addressing
echo "[+] Assigning IP addresses..."
ip netns exec ns_attacker ip addr add 192.168.100.10/24 dev veth_atk
ip netns exec ns_attacker ip link set veth_atk up
ip netns exec ns_attacker ip link set lo up

ip netns exec ns_receiver ip addr add 192.168.100.20/24 dev veth_rx
ip netns exec ns_receiver ip link set veth_rx up
ip netns exec ns_receiver ip link set lo up

# 7. Apply Physical Channel Emulation (Traffic Control / Netem)
# Emulate 5ms physical transport delay with 1.2ms jitter
echo "[+] Applying physical transport emulation (5ms delay +/- 1.2ms jitter)..."
ip netns exec ns_attacker tc qdisc add dev veth_atk root netem delay 5ms 1.2ms distribution normal

echo "[+] Verifying isolated connectivity..."
ip netns exec ns_attacker ping -c 2 192.168.100.20

echo "=== M6-B Isolated Network Environment Successfully Configured ==="
echo "Attacker Node: ip netns exec ns_attacker python3 attacker_vm_node.py"
echo "Receiver Node: ip netns exec ns_receiver python3 receiver_vm_node.py"
