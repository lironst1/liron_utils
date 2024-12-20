import warnings
import sys
import functools
import multiprocessing as mp
import threading
from queue import Queue
from tqdm import tqdm

NUM_CPUS = mp.cpu_count()
NUM_PROCESSES_TO_USE = NUM_CPUS
NUM_THREADS_TO_USE = 20


def parallel_map(func,
		iterable,
		callback=None,
		error_callback=None,
		num_processes: int = NUM_PROCESSES_TO_USE,
		desc: str = None,
		**kwargs) -> list:
	"""
	Run function 'func' in parallel.
	See qutip.parallel.parallel_map for reference.

	Notes
	-----
	- 'func' must be a global function (can't be nested inside another function).
	- parallel_map uses 'spawn' [1,2] by default in Windows, which starts a Python child process from scratch.
	  This means that everything not under an 'if __name__==__main__' block will be executed multiple times.
	- In UNIX we use 'fork'.

	References
	----------
	[1] https://stackoverflow.com/questions/64095876/multiprocessing-fork-vs-spawn/66113051#66113051
	[2] https://stackoverflow.com/questions/72935231/statements-before-multiprocessing-main-executed-multiple-times-python
	[3] https://superfastpython.com/multiprocessing-pool-issue-tasks

	Examples
	--------
	>>> import time
	>>> def func(iter, x, y):
	>>> 	time.sleep(1)
	>>> 	return (x + y) ** iter
	>>>
	>>> if __name__ == '__main__':
	>>> 	x = 1
	>>> 	y = 2
	>>> 	t0 = time.time()
	>>> 	out = parallel_map(func=func, iterable=range(100), num_processes=8, x=x, y=y)
	>>> 	print(out[:5])
	>>> 	print(f"time: {time.time() - t0}sec")

	Notes
	-----
	- If you get UserWarning: Can't pickle local object 'func.<locals>.func_partial', try to define 'func' in
	  the global scope.

	Parameters
	----------
	func :              callable
						The function to evaluate in parallel. The first argument is the changing value of each iteration
	iterable :          array_like
						First input argument for 'func'
	callback :          callable
						function to call after each iteration is done
	error_callback :    callable
						function to call if an error occurs
	num_processes :     int
						number of processes to use
	desc :              str
						description for tqdm
	kwargs :            passed to func

	Returns
	-------
	list of 'func' outputs, organized by the order of 'iter'.

	"""
	if sys.platform == 'darwin':  # in UNIX 'fork' can be used (faster but more dangerous)
		Pool = mp.get_context('fork').Pool
	else:  # In Windows only 'spwan' is available
		Pool = mp.Pool
		mp.Process()

	if num_processes > NUM_CPUS:
		warnings.warn(f"Requested number of processes {num_processes} is larger than number of CPUs {NUM_CPUS}.\n"
		              f"For better performance, consider reducing 'num_processes'.", category=UserWarning)
	num_processes = min(num_processes, NUM_CPUS, len(iterable))

	with Pool(processes=num_processes) as pool:
		func_partial = functools.partial(func, **kwargs)  # pass kwargs to func

		out_async = [pool.apply_async(
				func=func_partial,
				args=(i,),
				callback=callback,
				error_callback=error_callback
		) for i in iterable]

		out = []
		for out_async_i in tqdm(out_async, total=len(iterable), desc=desc):
			try:
				out += [out_async_i.get()]

			except KeyboardInterrupt as e:
				raise e

			except Exception as e:
				warnings.warn(str(e))

	return out


def parallel_threading(func,
		iterable,
		lock: bool = False,
		num_threads: int = NUM_THREADS_TO_USE,
		desc=None,
		**kwargs) -> list:
	"""
	Run function 'func' in parallel using threads.

	Parameters
	----------
	func :          callable
					The function to evaluate using threads. The first argument is the changing value of each iteration
	iterable :      array_like
					First input argument for 'func'
	lock :          bool
					use a lock to prevent concurrent access to shared resources
	num_threads :   int
					number of threads to use
	desc :          str or callable
					description for tqdm. If callable, should return a string.
	kwargs :        passed to func

	Returns
	-------
	list of 'func' outputs, organized by the order of 'iter'.
	"""

	if lock:
		lock = threading.Lock()
	if not callable(desc):
		desc_str = desc
		desc = lambda i: desc_str

	out = [None] * len(iterable)

	def worker(queue: Queue, pbar: tqdm):
		while True:
			index, item = queue.get()

			try:
				if lock:
					with lock:
						out[index] = func(item, **kwargs)
				else:
					out[index] = func(item, **kwargs)
				pbar.set_description(desc(index))
				pbar.update(1)

			except Exception as e:
				warnings.warn(str(e))

			queue.task_done()

	queue = Queue()
	threads = []
	with tqdm(total=len(iterable), desc=desc(0)) as pbar:
		for _ in range(num_threads):
			thread = threading.Thread(target=worker, args=(queue, pbar), daemon=True)
			thread.start()
			threads.append(thread)

		for index, item in enumerate(iterable):
			queue.put((index, item))

		queue.join()

	return out
