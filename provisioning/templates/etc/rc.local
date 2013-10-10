#!/bin/bash

# inspired by lcdev.dk

echo "Scanning for known WiFi networks"

connected=false

ssids=('{{ ap_ssid }}')

wlan_addr=`cat /sys/class/net/wlan0/address`

if [ $wlan_addr == '80:1f:02:be:d1:ae' ]; then
    wlan_ip="{{ ip_subnet }}.1"
elif [ $wlan_addr == '80:1f:02:be:d1:c9' ]; then
    wlan_ip="{{ ip_subnet }}.2"
else
    echo "No valid adapter present."
    exit 0
fi

createNetwork() {
    echo "Creating WiFi network"
    ifconfig wlan0 down
    ifconfig wlan0 $wlan_ip netmask 255.255.255.0 up
    /etc/init.d/isc-dhcp-server start
    /etc/init.d/hostapd start
}

connectNetwork() {
    for ssid in "${ssids[@]}"
    do
        if iwlist wlan0 scan | grep $ssid > /dev/null
        then
            echo "First WiFi in range has SSID:" $ssid
            echo "Starting supplicant for WPA/WPA2"
            wpa_supplicant -B -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf > /dev/null 2>&1

            echo "Obtaining IP from DHCP"
            if dhclient -1 wlan0
            then
                echo "Connected to WiFi"
                connected=true
                break
            else
                echo "DHCP server did not respond with an IP lease (DHCPOFFER)"
                wpa_cli terminate
                break
            fi
        else
            echo "Not in range, WiFi with SSID:" $ssid
        fi
    done
}



connectNetwork

# if we're not connected, sleep and give it one more shot before setting up as AP
if ! $connected; then
    wait_secs=`shuf -i 5-15 -n 1`
    echo "Sleeping $wait_secs seconds before retry."
    sleep $wait_secs
    connectNetwork
fi
if ! $connected; then
    createNetwork
fi

exit 0