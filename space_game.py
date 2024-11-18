import asyncio
import curses
import itertools
import os
import random
import time

from curses_tools import draw_frame, read_controls


SYMBOLS_FOR_STARS = '+*.:'
STARS_COUNT = 150
TIC_TIMEOUT = 0.1
BOARD_SIZE = 2


async def blink(canvas, row, column, animation_offset, symbol='*'):
    await sleep(animation_offset)

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(0.5)

        canvas.addstr(row, column, symbol)
        await sleep(0.3)


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
    double_ship_images = list(itertools.chain.from_iterable([[image] * 2 for image in ship_images]))
    cycle_images = itertools.cycle(double_ship_images)

    for ship_image in cycle_images:
        control = read_controls(canvas)
        row, column = get_ship_location(canvas, row, column, control, ship_image)
        draw_frame(canvas, row, column, ship_image)
        control = read_controls(canvas)
        row, column = get_ship_location(canvas, row, column, control, ship_image)
        draw_frame(canvas, row, column, ship_image, negative=True)
        await asyncio.sleep(0)


async def sleep(seconds):
    iteration_count = int(seconds * 10)
    for _ in range(iteration_count):
        await asyncio.sleep(0)


def load_images(directory_name):
    ship_images = []
    for filename in os.listdir(directory_name):
        file_path = os.path.join(directory_name, filename)
        with open(file_path, 'r', encoding='UTF-8') as file:
            ship_images.append(file.read())
    return ship_images


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])
    return rows, columns


def get_ship_location(canvas, current_row, current_column, controls, ship_image):
    rows, columns = canvas.getmaxyx()
    frame_rows, frame_columns = get_frame_size(ship_image)
    max_row, max_column = rows - frame_rows - 1, columns - frame_columns - 1
    controls_row, controls_column, _ = controls

    new_row = current_row + controls_row
    new_column = current_column + controls_column

    row = max(0, min(new_row, max_row))
    column = max(0, min(new_column, max_column))

    return row, column


def draw(canvas):
    ship_images = load_images('spaceship')
    curses.curs_set(False)
    canvas.border()
    canvas.nodelay(True)
    rows, columns = canvas.getmaxyx()

    frame_rows, frame_columns = get_frame_size(ship_images[0])
    ship_row = max(0, min(rows - frame_rows - 1, rows / 2 - frame_rows / 2))
    ship_column = max(0, min(columns - frame_columns - 1, columns / 2 - frame_columns / 2))

    coroutines = [
        blink(canvas, random.randint(1, rows - BOARD_SIZE),
              random.randint(1, columns - BOARD_SIZE),
              random.randint(1, 20),
              random.choice(list(SYMBOLS_FOR_STARS))) for _ in range(STARS_COUNT)
    ]

    coroutines.append(animate_spaceship(canvas,
                                        ship_row,
                                        ship_column,
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

