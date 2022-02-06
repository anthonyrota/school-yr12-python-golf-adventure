from random import randint
from collections import deque


def make_cave(width, height):
    grid = _make_grid(width, height)
    edges = {}

    def add_edge(x, y, p1, p2):
        def coord(x, y, p):
            if p == 1:
                dx = 1
                dy = 2
            if p == 2:
                dx = 2
                dy = 1
            if p == 3:
                dx = 1
                dy = 0
            if p == 4:
                dx = 0
                dy = 1
            return (x * 2 + dx, y * 2 + dy)

        c1 = coord(x, y, p1)
        c2 = coord(x, y, p2)

        edges[c1] = (edges[c1][0], c2) if c1 in edges else (c2, None)
        edges[c2] = (edges[c2][0], c1) if c2 in edges else (c1, None)

    for y in range(height - 1):
        for x in range(width - 1):
            case = (
                grid[y + 1][x]
                + (grid[y + 1][x + 1] << 1)
                + (grid[y][x + 1] << 2)
                + (grid[y][x] << 3)
            )

            if case == 1:
                add_edge(x, y, 1, 4)
            elif case == 2:
                add_edge(x, y, 1, 2)
            elif case == 3:
                add_edge(x, y, 2, 4)
            elif case == 4:
                add_edge(x, y, 2, 3)
            elif case == 5:
                add_edge(x, y, 1, 2)
                add_edge(x, y, 3, 4)
            elif case == 6:
                add_edge(x, y, 1, 3)
            elif case == 7:
                add_edge(x, y, 3, 4)
            elif case == 8:
                add_edge(x, y, 3, 4)
            elif case == 9:
                add_edge(x, y, 1, 3)
            elif case == 10:
                add_edge(x, y, 1, 4)
                add_edge(x, y, 2, 3)
            elif case == 11:
                add_edge(x, y, 2, 3)
            elif case == 12:
                add_edge(x, y, 2, 4)
            elif case == 13:
                add_edge(x, y, 1, 2)
            elif case == 14:
                add_edge(x, y, 1, 4)

    polygons = [[]]
    c1, (c2, _) = next(iter(edges.items()))
    while True:
        polygons[-1].append(c1)
        del edges[c1]
        if c2 in edges:
            c2a, c2b = edges[c2]
            c1, c2 = c2, c2b if c2a == c1 else c2a
        elif len(edges) > 0:
            polygons.append([])
            c1, (c2, _) = next(iter(edges.items()))
        else:
            break

    for polygon in polygons:
        double_signed_area = 0
        for i, c1 in enumerate(polygon):
            c2 = polygon[(i + 1) % len(polygon)]
            double_signed_area += (c2[0] - c1[0]) * (c2[1] + c1[1])
        if double_signed_area > 0:
            polygon.reverse()  # make counter-clockwise

    return polygons


def _make_grid(
    width,
    height,
):
    wall_chance = 40
    min_surrounding_walls = 5
    iterations = 5
    pillar_iterations = 5
    min_open_percent = 0.25

    def do_cellular_automata(grid, make_pillars):
        updated_grid = [row[:] for row in grid]

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                count = (
                    grid[y - 1][x - 1]
                    + grid[y - 1][x]
                    + grid[y - 1][x + 1]
                    + grid[y][x - 1]
                    + grid[y][x]
                    + grid[y][x + 1]
                    + grid[y + 1][x - 1]
                    + grid[y + 1][x]
                    + grid[y + 1][x + 1]
                )
                is_wall = count >= min_surrounding_walls or (
                    make_pillars and count == 0
                )
                updated_grid[y][x] = 1 if is_wall else 0

        return updated_grid

    def copy_largest_open_space_into_new_grid(grid):
        def copy_open_space_into_new_grid(start_x, start_y):
            grid_with_single_open_space = [
                [1 for _ in range(width)] for _ in range(height)
            ]
            grid_with_single_open_space[start_y][start_x] = 0
            cell_coordinates_to_visit = deque([(start_x, start_y)])
            open_count = 1

            def check_empty(x, y):
                nonlocal open_count
                if grid[y][x] == 0 and grid_with_single_open_space[y][x] == 1:
                    grid_with_single_open_space[y][x] = 0
                    cell_coordinates_to_visit.append((x, y))
                    open_count += 1

            while len(cell_coordinates_to_visit) > 0:
                x, y = cell_coordinates_to_visit.popleft()
                grid_with_single_open_space[y][x] = 0
                check_empty(x - 1, y)
                check_empty(x + 1, y)
                check_empty(x, y - 1)
                check_empty(x, y + 1)

            return (grid_with_single_open_space, open_count)

        isolated_open_space_grids = []

        for start_y in range(1, height - 1):
            for start_x in range(1, width - 1):
                if grid[start_y][start_x] == 0 and all(
                    t[0][start_y][start_x] == 1 for t in isolated_open_space_grids
                ):
                    isolated_open_space_grids.append(
                        copy_open_space_into_new_grid(start_x, start_y)
                    )

        return max(isolated_open_space_grids, key=lambda t: t[1])

    while True:
        grid = [[0 for _ in range(width)] for _ in range(height)]

        for y in range(height):
            for x in range(width):
                if (
                    x == 0
                    or y == 0
                    or x == width - 1
                    or y == height - 1
                    or randint(0, 100) <= wall_chance
                ):
                    grid[y][x] = 1

        for _ in range(pillar_iterations):
            grid = do_cellular_automata(grid, make_pillars=True)

        for _ in range(iterations):
            grid = do_cellular_automata(grid, make_pillars=False)

        found_open = False
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                if grid[y][x] == 0:
                    found_open = True
                    break
            if found_open:
                break
        if not found_open:
            continue

        (
            grid_with_single_open_space,
            open_count,
        ) = copy_largest_open_space_into_new_grid(grid)
        if open_count >= min_open_percent * width * height:
            return grid_with_single_open_space