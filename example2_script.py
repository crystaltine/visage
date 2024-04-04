from interpreter import read_styles, read_vis
from globalvars import Globals

read_styles("example2.tss")
read_vis("example2.vis")

document = Globals.__vis_document__
document.mount()

last_w = document.term.width
last_h = document.term.height

while 1:
    curr_w = document.term.width
    curr_h = document.term.height

    if (curr_w != last_w) or (curr_h != last_h):
        # dims changed, rerender and remomorize
        last_w = document.term.width
        last_h = document.term.height
        document.client_right = document.term.width
        document.client_bottom = document.term.height
        document.render()