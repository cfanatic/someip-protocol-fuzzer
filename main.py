from someip_fuzzer.config import config
from someip_fuzzer.fuzzer import Fuzzer
from someip_fuzzer.heartbeat import Heartbeat
from someip_fuzzer.log import log_info, log_error
from someip_fuzzer.template import *
from someip_fuzzer.types import *
from queue import Queue
import signal
import time

def generate_template():
    generator = Template()
    packets = generator.read_capture()
    trace = generator.create_template(packets)
    generator.save_template(trace)
    log_info("Printing JSON dump")
    generator.print_template(trace)

def import_template():
    generator = Template()
    trace = generator.read_template()
    return trace

def shutdown(signum, frame):
    raise ServiceShutdown("Caught signal %d" % signum)

def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    excq = Queue()
    targets = []
    threads = []

    template = import_template()
    fields = template[(True, config["Fuzzer"]["Layer"])]["fields"].items()
    for fieldname, fieldvalues in fields:
        fuzzer = fieldvalues["fuzzing"]["fuzzer"]
        if fuzzer is not None:
            targets.append((fieldname, fuzzer))
            log_info("Fuzzing protocol layer '{}' on protocol field '{}'".format(config["Fuzzer"]["Layer"], fieldname))

    if config["Fuzzer"]["Mode"] == "replay":
        try:
            threads.append(Heartbeat(excq))
            for i in range(len(targets)):
                threads.append(Fuzzer(i, excq, template, targets[i]))
            for t in threads:
                t.start()
            while True:
                if excq.qsize() != 0:
                    raise excq.get()
        except (NoHostError, NoHeartbeatError, NoSudoError) as exc:
            log_error(exc)
        except ServiceShutdown as msg:
            log_info(msg)
        finally:
            for t in threads:
                t.shutdown.set()
                t.join()
            log_info("Exiting main()")
    elif config["Fuzzer"]["Mode"] == "live":
        pass

if __name__ == "__main__":
    main()
