from LocalChecker import LocalChecker

green_colors = [
    [21, 117, 21]
]
red_colors = [
    [145, 2, 2],
    [147, 4, 4],
    [193, 69, 2],
    [195, 71, 4],
    [193, 136, 2],
    [195, 138, 4]
]

LC = LocalChecker(structure_mode='mouse', structure_name='Fortizar', start_timeout=5, red_colors=red_colors)
LC.choose_area()
LC.check_local(signal=True, warp_out=True)
