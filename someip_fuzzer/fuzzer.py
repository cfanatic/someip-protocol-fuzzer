from scapy.all import *
from someip_fuzzer.config import config
from someip_fuzzer.log import log_info
from someip_fuzzer.types import *
from queue import Queue
import binascii
import random
import threading
import time
import subprocess

class Fuzzer(threading.Thread):

    def __init__(self, index, excq, template, targets):
        super().__init__()
        self.index = index
        self.excq = excq
        self.template = template
        self.targets = targets
        self.shutdown = threading.Event()
    
    def run(self):
        log_info("Thread #{} is started".format(self.index))
        while not self.shutdown.is_set():
            time.sleep(1) # this value must be set according to the available bandwidth
            value = self.prepare()
            self.send(value)
        log_info("Thread #{} is stopped".format(self.index))

    def prepare(self):
        if self.shutdown.is_set():
            return
        fields = self.template[(True, config["Fuzzer"]["Layer"])]["fields"]
        target = self.targets[0]
        index = random.choice(range(len(fields[target]["values"])))
        value = fields[target]["values"][index]
        p = subprocess.Popen(
            ["radamsa"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        if isinstance(value, str):
            value_convert = binascii.unhexlify(value) # convert hex -> 48656c6c6f205365727669636521 to ascii -> b'Hello Service!'
        else:
            value_convert = value
        value_fuzz = p.communicate(input=value_convert)[0]
        if config["Fuzzer"]["History"] == "yes":
            log_info("Saving current fuzzing value as next seed")
            fields[target]["values"][index] = value_fuzz
        return value_fuzz

    def send(self, value):
        log_info("Sending: {}".format(value))
        i = IP(src=config["Client"]["Host"], dst=config["Service"]["Host"])
        u = UDP(sport=config["Client"].getint("Port"), dport=config["Service"].getint("Port"))
        sip = SOMEIP()
        sip.iface_ver = 0
        sip.proto_ver = 1
        sip.msg_type = "REQUEST"
        sip.retcode = "E_OK"
        sip.msg_id.srv_id = 0x1234
        sip.msg_id.sub_id = 0x0
        sip.msg_id.method_id=0x0421
        sip.req_id.client_id = 0x1313
        sip.req_id.session_id = 0x0010
        sip.add_payload(Raw (value))
        paket = i/u/sip
        res = sr1(paket, retry=0, timeout=1, verbose=False)
    