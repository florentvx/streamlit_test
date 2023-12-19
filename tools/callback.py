from __future__ import annotations
import queue
import asyncio

MY_QUEUES: dict[str, queue.Queue] = {}

def init_queue(page: str):
    if page not in MY_QUEUES.keys():
        print("my queue is added")
        MY_QUEUES[page] = queue.Queue()

    def add_item_to_queue(task):
        def new_fct():
            print("PUT IN Q")
            MY_QUEUES[page].put(task)
        return new_fct

    async def callback_loop():
        print(f"QUEUE STATE: {MY_QUEUES[page].empty()}")
        if MY_QUEUES[page].empty():
            return False
        
        my_timer = 0.2
        while my_timer > 0:
            while not MY_QUEUES[page].empty():
                task = MY_QUEUES[page].get()
                print(f"Doing {task.__name__}")
                await task()
            await asyncio.sleep(0.1)
            my_timer -= 0.1
        print(f"BIS - QUEUE STATE: {MY_QUEUES[page].empty()}")
        return True
    return add_item_to_queue, callback_loop