# someip-protocol-fuzzer

This repository features a proof-of-concept for a SOME/IP network protocol fuzzer.

What it does is quite simple: It mutates user-defined protocol fields using [radamsa](https://gitlab.com/akihe/radamsa).

Implemented is a heartbeat mechanism which checks whether the target service on the other end is still responding. If not, fuzzing will be terminated.

The current state is a black-box approach. In order to improve the attack potential in grey-box fashion, one would need to implement a state machine. You want to initialize the session in a way that the fuzzer is able to pass the most trivial checks on the target service first.

## Requirements

It is recommended to use two VMs which run any version of GNU/Linux each.

| VM #1 - Target     | VM #2 - Fuzzer     |
| ------------------ | ------------------ |
| CMake 3.16.3       | Python 3.7.6       |
| vsomeip 3.1.20     | scapy 2.4.5        |
| boost 1.65.1       | radamsa 0.6        |

## Setup

The instructions below describe how to configure the VMs for the target service and protocol fuzzer. The default configuration assumes that 192.168.0.18 is the IP address on VM #1, and 192.168.0.19 on VM #2.

### VM #1 - Target

Clone [vsomeip-fuzzing](https://github.com/cfanatic/vsomeip-fuzzing), and follow the build instructions in sections [4. Build library](https://github.com/cfanatic/vsomeip-fuzzing#4-build-library) and [5. Build target](https://github.com/cfanatic/vsomeip-fuzzing#5-build-target). Call `make response` to build a SOME/IP service as the fuzzing target.

Copy the [service configuration file](https://github.com/cfanatic/vsomeip-fuzzing/blob/master/conf/vsomeip_response.json) into the build folder next to `response`, and name it `vsomeip.json`. Adjust the IP address configuration field accordingly.

When you run `./response`, the output must show something similar to:

```log
2022-02-18 14:59:28.396999 [info] Parsed vsomeip configuration in 0ms
2022-02-18 14:59:28.397593 [info] Using configuration file: "./vsomeip.json".
2022-02-18 14:59:28.397751 [info] Initializing vsomeip application "!!SERVICE!!".
2022-02-18 14:59:28.398101 [info] Instantiating routing manager [Host].
2022-02-18 14:59:28.398342 [info] create_local_server Routing endpoint at /tmp/vsomeip-0
2022-02-18 14:59:28.398740 [info] Service Discovery enabled. Trying to load module.
2022-02-18 14:59:28.400098 [info] Service Discovery module loaded.
2022-02-18 14:59:28.400516 [info] Application(!!SERVICE!!, 1212) is initialized (11, 100).
2022-02-18 14:59:28.400694 [info] Starting vsomeip application "!!SERVICE!!" (1212)
2022-02-18 14:59:28.401511 [info] main dispatch thread id from application: 1212 (!!SERVICE!!)
2022-02-18 14:59:28.403643 [info] io thread id from application: 1212 (!!SERVICE!!)
2022-02-18 14:59:28.402029 [info] shutdown thread id from application: 1212 (!!SERVICE!!)
2022-02-18 14:59:28.402721 [info] Watchdog is disabled!
2022-02-18 14:59:28.404079 [info] vSomeIP 3.1.20.3 | (default)
2022-02-18 14:59:28.403850 [info] OFFER(1212): [1234.5678:0.0] (true)
2022-02-18 14:59:28.404343 [info] Network interface "eth0" state changed: up
2022-02-18 14:59:28.406458 [info] Route "default route (0.0.0.0/0) if: eth0 gw: 192.168.0.1"
2022-02-18 14:59:28.407549 [debug] Joining to multicast group 224.224.224.245 from 192.168.0.18
2022-02-18 14:59:28.407767 [info] udp_server_endpoint_impl: SO_RCVBUF (Multicast) is: 212992
2022-02-18 14:59:28.411331 [info] SOME/IP routing ready.
```

### VM #2 - Fuzzer

Clone [someip-protocol-fuzzer](https://github.com/cfanatic/someip-protocol-fuzzer), and run following instructions:

```bash
virtualenv -p python3 .venv
source .venv/bin/activate
pip3 install -r requirements.txt 
```

Open the [fuzzer configuration file](https://github.com/cfanatic/someip-protocol-fuzzer/blob/master/config.ini), and adjust the IP address configuration fields accordingly. Same for the source and destination ports. You can find this out using Wireshark.

Finally, install [radamsa](https://gitlab.com/akihe/radamsa).

When you run `sudo python3 main.py`, the output must show something similar to:

```log
15:13:15 INFO: Fuzzing protocol layer 'SOMEIP' on protocol field 'load'
15:13:15 INFO: Heartbeat is started
15:13:15 INFO: Thread #0 is started
15:13:16 INFO: Sending: b'Hell\\nSril\\nSril\\nService!ervice!ervice!ervice!'
15:13:17 INFO: Sending: b'o SService!'
15:13:18 ERROR: No heartbeat found on SOME/IP service
15:13:21 INFO: Heartbeat is stopped
15:13:21 INFO: Thread #0 is stopped
15:13:21 INFO: Exiting main()
```

## Usage

n/a
