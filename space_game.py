import asyncio
import curses
import os
import random
import time

from curses_tools import draw_frame, read_controls


SYMBOLS_FOR_STARS = '+*.:'
STARS_COUNT = 150
TIC_TIMEOUT = 0.1
BOARD_SIZE = 2


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


async def animate_spaceship(canvas, row, column, ship_images):
    while True:
        control = read_controls(canvas)
        for ship_image in ship_images:
            row, column = get_ship_location(row, column, control)
            draw_frame(canvas, row, column, ship_image)
            for i in range(2):
                await asyncio.sleep(0)
            draw_frame(canvas, row, column, ship_image, negative=True)


def load_images(directory_name):
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


def get_ship_location(current_row, current_column, control):
    control_row, control_column, _ = control
    new_row = current_row + control_row
    new_column = current_column + control_column
    return new_row, new_column


def draw(canvas):
    ship_images = load_images('spaceship')
    curses.curs_set(0)
    canvas.border()
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()
    coroutines = [
        blink(canvas, random.randint(1, rows - BOARD_SIZE),
              random.randint(1, columns - BOARD_SIZE),
              random.randint(1, 20),
              random.choice(list(SYMBOLS_FOR_STARS))) for _ in range(STARS_COUNT)
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
        time.sleep(TIC_TIMEOUT)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)

