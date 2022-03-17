from scapy.all import *
from someip_fuzzer.config import config
from someip_fuzzer.log import log_info
from someip_fuzzer.types import *
from queue import Queue
import threading
import time

load_contrib("automotive.someip")

class Heartbeat(threading.Thread):

    def __init__(self, excq):
        super().__init__()
        self.excq = excq
        self.shutdown = threading.Event()
       
    def run(self):
        log_info("Heartbeat is started")
        while not self.shutdown.is_set():
            try:
                time.sleep(3)
                self.check()
            except PermissionError:
                self.excq.put(NoSudoError("Permission as sudo required to send SOME/IP pakets"))
        log_info("Heartbeat is stopped")

    def check(self):
        try:
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
            sip.add_payload(Raw ("ping"))
            paket = i/u/sip
            res = sr1(paket, retry=0, timeout=3, verbose=False)
            if res == None:
                raise NoHostError("No response received from SOME/IP host")
            if res[Raw].load[-4:] != bytes("pong", "utf-8"):
                raise NoHeartbeatError("No heartbeat found on SOME/IP service")
        except (NoHostError, NoHeartbeatError) as exc:
                self.excq.put(exc)
