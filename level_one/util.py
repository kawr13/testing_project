import time
import asyncio
import sys

async def print_fib(number: int) -> None:
    def fib(n: int) -> int:
        if n == 1:
            return 0
        elif n == 2:
            return 1
        else:
            print(f'Выполнение асинхронной задачи {asyncio.current_task()}')
            return fib(n - 1) + fib(n - 2)
    print(f'fib({number}) равно {fib(number)}')


async def fibs_no_threading():
    task = [asyncio.create_task(await print_fib(i)) for i in range(40, 41 + 1)]
    await asyncio.gather(*task)


async def main():
    start = time.time()
    task = asyncio.create_task(fibs_no_threading())
    await task
    end = time.time()
    print(f'Время работы {end - start:.4f} с.')


if __name__ == '__main__':
    asyncio.run(main())