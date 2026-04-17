"""
Version 2.1
Module: mlx_renderer
mambo.
"""


from mlx import Mlx  # type: ignore


def draw_42_pattern(data, sl, cell_size, window_width, window_height):
    """Draw the '42' pattern using fully closed cells."""
    pattern_42 = [
        [1, 0, 1, 0, 1, 1, 1],
        [1, 0, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 1, 1],
        [1, 1, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    pattern_width = len(pattern_42[0]) * cell_size
    pattern_height = len(pattern_42) * cell_size
    start_x = (window_width - pattern_width) // 2
    start_y = (window_height - pattern_height) // 2
    for row in range(len(pattern_42)):
        for col in range(len(pattern_42[row])):
            if pattern_42[row][col] == 1:
                cell_x = start_x + (col * cell_size)
                cell_y = start_y + (row * cell_size)
                for py in range(cell_size):
                    for px in range(cell_size):
                        pixel_x = cell_x + px
                        pixel_y = cell_y + py
                        offset = (pixel_y * sl) + (pixel_x * 4)
                        data[offset:offset+4] = (0xFFFF0000).to_bytes(
                            4, 'little')


m = Mlx()
mlx_ptr = m.mlx_init()
win_ptr = m.mlx_new_window(mlx_ptr, 600, 600, "A-Maze-ing")
img = m.mlx_new_image(mlx_ptr, 600, 600)
data, bpp, sl, iformat = m.mlx_get_data_addr(img)
m.mlx_string_put(mlx_ptr, win_ptr, 20, 20, 255, "Hello PyMlx!")
draw_42_pattern(data, sl, 15, 600, 600)
m.mlx_put_image_to_window(mlx_ptr, win_ptr, img, 0, 0)


def mouse_handler(button, x, y, mystuff):
    print(f"Got mouse event! button {button} at {x},{y}.")


def key_handler(keynum, mystuff):
    print(f"Got key {keynum}, and got my stuff back:")
    print(mystuff)
    if keynum == 32:
        m.mlx_mouse_hook(win_ptr, None, None)


def close_handle(dummy):
    m.mlx_loop_exit(mlx_ptr)


m.mlx_mouse_hook(win_ptr, mouse_handler, None)
m.mlx_key_hook(win_ptr, key_handler, None)
m.mlx_hook(win_ptr, 33, 0, close_handle, None)

m.mlx_loop(mlx_ptr)
