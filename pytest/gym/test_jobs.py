from queue import Queue


def test():
    a = Queue()
    a.put(1)
    a.put(2)
    a.put(3)
    for job in iter(a.get, 3):
        print(job)
