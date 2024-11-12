import asyncio
import curses
import time


class EventLoopCommand():

    def __await__(self):
        return (yield self)


class Sleep(EventLoopCommand):

    def __init__(self, seconds):
        self.seconds = seconds


async def go_to_sleep(sec):
    sleep_time = Sleep(sec)
    await sleep_time


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await go_to_sleep(2)

        canvas.addstr(row, column, symbol)
        await go_to_sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await go_to_sleep(0.5)

        canvas.addstr(row, column, symbol)
        await go_to_sleep(0.3)


def draw(canvas):
    curses.curs_set(0)
    canvas.border()
    rows = [5, 6, 7, 8, 9]
    columns = [20, 20, 20, 20, 20]
    coroutines = [blink(canvas, row, column) for row, column in zip(rows, columns)]
    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        time.sleep(0.4)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
