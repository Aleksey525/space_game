import asyncio
import curses
import os
import random
import time


from curses_tools import draw_frame


SYMBOLS_FOR_STARS = '+*.:'


async def blink(canvas, row, column, animation_offset, symbol='*'):
    for _ in range(int(animation_offset * 10)):
        await asyncio.sleep(0)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range (2 * 10):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3):
            await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot, direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, row, column, images):
    while True:
        for image in images:
            draw_frame(canvas, row, column, image)
            for i in range(2):
                await asyncio.sleep(0)
            draw_frame(canvas, row, column, image, negative=True)


def load_ship(directory_name):
    ship_images = []
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        print(file_path)
        with open(file_path, 'r', encoding='UTF-8') as file:
            ship_images.append(file.read())
    return ship_images


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def draw(canvas):
    ship_images = load_ship('spaceship')
    curses.curs_set(0)
    canvas.border()
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    coroutines = [
        blink(canvas, random.randint(1, rows - 3),
              random.randint(1, columns - 3),
              random.randint(1, 20),
              random.choice(list(SYMBOLS_FOR_STARS))) for _ in range(150)
    ]

    coroutines.append(animate_spaceship(canvas,
                                        rows - 10,
                                        columns / 2 - 2,
                                        ship_images)
                      )

    coroutines.append(fire(canvas, rows / 2, columns / 2))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        time.sleep(0.1)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

