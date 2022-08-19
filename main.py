### Imports ###
import sys, queue, threading, requests, datetime
from colorama import Fore,init

### Variables ###
init()
input_queue = queue.Queue()
result_queue = queue.Queue()
thread_lock = threading.Lock()
date_time = datetime.datetime.now()
current_time = date_time.time()

INFO = "[\x1b[33m?\x1b[37m] "
ERROR = "[\x1b[31m-\x1b[37m] "
SUCCESS = "[\x1b[32m+\x1b[37m] "

### Editable Variables ###

timeout_period = 1

class ProcessThread(threading.Thread):
    def __init__(self, in_queue, out_queue):
        threading.Thread.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        while True:
            result = self.process(self.in_queue.get())
            if (result is not None):
                self.out_queue.put(result)

            self.in_queue.task_done()

    def process(self, proxy):
        clean_proxy = proxy.replace("\n", "")
        try:
            proxy_formatter = {
                "http": "http://" + clean_proxy,
                "https": "http://" + clean_proxy
            }
            r = requests.get("http://ipinfo.io/json", proxies=proxy_formatter, timeout=timeout_period)
            printableOutput = (Fore.GREEN + '[%s:%s:%s]  %s' % (current_time.hour, current_time.minute, current_time.second , r.json()["ip"]))
            with thread_lock:
                print(printableOutput)

                return "%s" % (proxy)
        except:
            with thread_lock:
                print(Fore.RED + '[%s:%s:%s]  %s' % (current_time.hour, current_time.minute, current_time.second , clean_proxy))
            return None

    def terminate(self):    
        None


class LogWorking(threading.Thread):
	def __init__(self, queue, output_file):
		threading.Thread.__init__(self)
		self.queue = queue
		self.output = open(output_file, "a")
		self.shutdown = False

	def log(self, string):
		print(string, file=self.output)

	def run(self):
		while not self.shutdown:
			self.log(self.queue.get())
			self.queue.task_done()

	def terminate(self):
		self.output.close()
		self.shutdown = True


def main():
	# Check Argument Length
	if (len(sys.argv) < 4):
		print("%s Incorrect usage!" % (ERROR))
		print("%s Usage: %s <proxy list> <threads> <output file>" % (INFO, sys.argv[0]))
		exit(1)

	try:
		ip_list = [line.rstrip("\n") for line in open(sys.argv[1], "r")]
	except BaseException as error:
		print(str(error))
		exit(1)

	# Check If File Is Empty
	if (len(ip_list) == 0):
		print("%s Chosen file is blank" % (ERROR))
		exit(1)

	# Load Input Queue
	i = 0
	for ip in ip_list:
		input_queue.put(ip)
		i += 1
		sys.stdout.write("\rAdded %d proxies to queue" % (i))
		sys.stdout.flush()

	print("\n\n%s Checking %d proxies" % (INFO, len(ip_list)))

	# Start Workers
	workers = []
	for i in range(0, int(sys.argv[2])):
		thread = ProcessThread(input_queue, result_queue)
		thread.daemon = True
		thread.start()
		workers.append(thread)

	logger = LogWorking(result_queue, sys.argv[3])
	logger.daemon = True
	logger.start()

	# Wait until our queues are finished
	input_queue.join()
	result_queue.join()
	logger.terminate()
	for worker in workers:
		worker.terminate()


if (__name__ == "__main__"):
	main()
