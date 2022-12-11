#!/usr/bin/env python3

import socket
import time

import requests
import socks
from stem import Signal
from stem.control import Controller

# # get page and extract unique key
url = "https://vote.easypolls.net/623b3ca83070840062eb0822"
get_headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0"
}

post_url = "https://vote.easypolls.net/api/vote/623b3ca83070840062eb0822"
post_headers = {"Content-type": "application/json", "Accept": "text/plain"}


# https://www.torproject.org/docs/faq.html.en#torrc
# https://stem.torproject.org/tutorials/the_little_relay_that_could.html
# https://stackoverflow.com/questions/9887505/how-to-change-tor-identity-in-python
# sudo pip3 install stem
# sudo apt-get install tor
# generate new password for tor > tor --hash-password "<new_password>"
# save new password hash -> /etc/tor on line -> HashedControlPassword
# uncomment HashedControlPassword and ControlPort
# restart tor service -> /etc/init.d/tor restart -> sudo service tor restart


def changeIp(current_ip):
    controller.signal(Signal.NEWNYM)
    time.sleep(controller.get_newnym_wait())


def vote(times=3):
    # we can vote 3 times in a row from the same IP, before hitting a wait-period
    for i in range(times):
        s = requests.Session()
        res = s.get(url, headers=get_headers)
        content = res.content.decode()
        idx = content.find("key:")
        key = content[idx + 5 : idx + 5 + 7]
        print(key)

        time.sleep(1)

        data = {"choices": [2], "ticket": "", "key": key}
        r = s.post(post_url, headers=post_headers, json=data)
        print(r.status_code, r.reason, r.content)
        del s


with Controller.from_port(port=9051) as controller:
    current_ip = requests.get(url="http://icanhazip.com/")
    print(current_ip.text)
    vote()

    controller.authenticate(password="abc123")
    socks.setdefaultproxy(
        proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050
    )
    socket.socket = socks.socksocket
    for i in range(1500):
        changeIp(current_ip.text)
        current_ip = requests.get(url="http://icanhazip.com/")
        print(current_ip.text)
        vote()
