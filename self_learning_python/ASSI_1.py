

import math
import turtle

import easygui

APP_TITLE = "Geometric Art Studio"
SHAPES = ["Square", "Equilateral Triangle", "Concentric Circles", "Custom Star"]
MIN_SIZE, MAX_SIZE = 50, 250
DEFAULT_SIZE = 150
DEFAULT_COLOR = "blue"



def choose_shape():
    #Show the shape menu. Returns the chosen shape name or none 
    return easygui.buttonbox(
        msg="Which shape would you like to draw?",
        title=APP_TITLE,
        choices=SHAPES,
    )


def ask_size(shape):
    #will ask for dimension 
    label = "radius" if shape in ("Concentric Circles", "Custom Star") else "side length"
    return easygui.integerbox(
        msg=f"Enter the {label} in pixels ({MIN_SIZE} to {MAX_SIZE}):",
        title=APP_TITLE,
        default=DEFAULT_SIZE,
        lowerbound=MIN_SIZE,
        upperbound=MAX_SIZE,
    )


def ask_color():
    #will ask for the colour
    return easygui.enterbox(
        msg='Enter a fill color (e.g. "blue", "red", "teal") or a hex code like #ff8800:',
        title=APP_TITLE,
        default=DEFAULT_COLOR,
    )


def is_valid_color(color):
    """Return True if turtle/Tk understands this color string."""
    try:
        turtle.Screen().getcanvas().winfo_rgb(color)
        return True
    except Exception:
        return False



def setup_canvas():
    #creating the drawing window and turtle with appropiate speed
    screen = turtle.Screen()
    screen.title(APP_TITLE)
    screen.setup(width=700, height=700)
    screen.bgcolor("white")

    pen = turtle.Turtle()
    pen.speed(3)          
    pen.pensize(3)
    pen.pencolor("black")
    return screen, pen


#
def draw_filled_polygon(pen, points, color):
    """Draw a closed polygon through the given (x, y) points and fill it."""
    pen.penup()
    pen.goto(points[0])
    pen.fillcolor(color)
    pen.pendown()
    pen.begin_fill()
    for point in points[1:]:
        pen.goto(point)
    pen.goto(points[0])   # close the shape
    pen.end_fill()
    pen.penup()



def draw_square(pen, side, color):
    """Square centred on the origin."""
    half = side / 2
    points = [(-half, -half), (half, -half), (half, half), (-half, half)]
    draw_filled_polygon(pen, points, color)


def draw_triangle(pen, side, color):
    """Equilateral triangle centred (vertically) on the origin."""
    height = side * math.sqrt(3) / 2
    points = [
        (-side / 2, -height / 3),   # bottom-left
        (side / 2, -height / 3),    # bottom-right
        (0, 2 * height / 3),        # top apex
    ]
    draw_filled_polygon(pen, points, color)


def draw_concentric_circles(pen, radius, color, rings=5):
    """Concentric circles from the outside in, alternating color and white."""
    for i in range(rings):
        r = radius * (rings - i) / rings
        ring_color = color if i % 2 == 0 else "white"
        pen.penup()
        pen.goto(0, -r)       # turtle.circle() starts at the bottom of the circle
        pen.setheading(0)
        pen.fillcolor(ring_color)
        pen.pendown()
        pen.begin_fill()
        pen.circle(r)
        pen.end_fill()
        pen.penup()


def draw_star(pen, radius, color, tips=5, inner_ratio=0.382):
    """Star whose outer tips lie on a circle of the given radius."""
    inner_radius = radius * inner_ratio
    points = []
    for i in range(tips * 2):
        angle = math.pi / 2 + i * math.pi / tips     # start with a tip pointing up
        r = radius if i % 2 == 0 else inner_radius
        points.append((r * math.cos(angle), r * math.sin(angle)))
    draw_filled_polygon(pen, points, color)



SHAPE_DRAWERS = {
    "Square": draw_square,
    "Equilateral Triangle": draw_triangle,
    "Concentric Circles": draw_concentric_circles,
    "Custom Star": draw_star,
}



def main():
    shape = choose_shape()
    if shape is None:
        return

    size = ask_size(shape)
    if size is None:
        return

    color = ask_color()
    if color is None:
        return
    color = color.strip() or DEFAULT_COLOR

    if not is_valid_color(color):
        easygui.msgbox(
            f'"{color}" is not a color I recognise, so I will use {DEFAULT_COLOR} instead.',
            title=APP_TITLE,
        )
        color = DEFAULT_COLOR

    screen, pen = setup_canvas()
    try:
        SHAPE_DRAWERS[shape](pen, size, color)
        pen.hideturtle()
        easygui.msgbox(
            f"Done! Your {color} {shape.lower()} is complete.\n\n"
            "Click OK to close the drawing window.",
            title=APP_TITLE,
        )
    except (turtle.Terminator, Exception):
        # The user closed the turtle window mid-drawing; nothing more to do.
        pass
    finally:
        try:
            turtle.bye()
        except Exception:
            pass


if __name__ == "__main__":
    main()