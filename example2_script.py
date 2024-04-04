from interpreter import read_styles, read_vis
from globalvars import Globals

read_styles("example2.tss")
read_vis("example2.vis")

document = Globals.__vis_document__
document.mount()