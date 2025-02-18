import random
import tkinter as tk

from TIN import *
from MapGeneration import *


class MainWindow:
    # radius of drawn points on canvas
    RADIUS = 3

    # flag to lock the canvas when drawn
    LOCK_FLAG = False
    
    def __init__(self, master):
        self.master = master
        self.master.title("Voronoi")

        self.width = 1200
        self.height = 800
        self.num_points = 2000
        self.updates = 1

        self.frmMain = tk.Frame(self.master, relief=tk.RAISED, borderwidth=1)
        self.frmMain.pack(fill=tk.BOTH, expand=1)

        self.w = tk.Canvas(self.frmMain, width=self.width, height=self.height)
        self.w.config(background='white')
        self.w.bind('<Button-1>', self.onClick)
        self.w.pack()       

        self.frmButton = tk.Frame(self.master)
        self.frmButton.pack()
        
        self.btnGenerate = tk.Button(self.frmButton, text="Generate Map", width=25, command=self.onClickMapGeneration)
        self.btnGenerate.pack(side=tk.LEFT)
        
        self.btnClear = tk.Button(self.frmButton, text='Clear', width=25, command=self.onClickClear)
        self.btnClear.pack(side=tk.LEFT)
        
    def onClickMapGeneration(self):
        if not self.LOCK_FLAG:
            self.LOCK_FLAG = True
            points = []
            for _ in range(self.num_points):
                x = random.random() * self.width
                y = random.random() * self.height
                points.append(Site(x, y))
            map_generation = MapGeneration(self.width, self.height, points, min_latitude=-1, max_latitude=1, island_num=5)
            for _ in range(self.updates):
                map_generation.updatePoints()
            self.w.delete(tk.ALL)
            map_generation.process()
            map_generation.generateDistricts()
            districts = map_generation.getDistricts()
            lines = map_generation.coastlines + map_generation.rivers
            self.drawMapOnCanvas(districts, lines)
    
    def onClickPointGeneration(self):
        if not self.LOCK_FLAG:
            random_sites = []
            for _ in range(self.num_points):
                x = random.random() * self.width
                y = random.random() * self.height
                random_sites.append(Site(x, y))
            self.drawSitesOnCanvas(random_sites)
    
    def drawSitesOnCanvas(self, sites):
        for site in sites:
            self.w.create_oval(site.x-self.RADIUS, site.y-self.RADIUS, site.x+self.RADIUS, site.y+self.RADIUS, fill="black")

    def onClickClear(self):
        self.LOCK_FLAG = False
        self.w.delete(tk.ALL)

    def onClick(self, event):
        if not self.LOCK_FLAG:
            self.w.create_oval(event.x-self.RADIUS, event.y-self.RADIUS, event.x+self.RADIUS, event.y+self.RADIUS, fill="black")

    def drawTriangleOnCanvas(self, edge):
        edge._qedge.mark = 1
        # draw edge
        p0 = edge.org()
        p1 = edge.dest()
        p2 = edge.lnext().dest()
        self.w.create_line(p0.x, p0.y, p1.x, p1.y, fill='blue')

        # recurse to the left face edges
        ledge= edge.onext()
        if ledge._qedge.mark == 0:
            self.drawTriangleOnCanvas(ledge)
        redge = edge.lnext().sym()
        if redge._qedge.mark == 0:
            self.drawTriangleOnCanvas(redge)
        # take the opposite edge
        edge = edge.sym()
        # recurse to the rightface edges
        ledge = edge.onext()
        if ledge._qedge.mark == 0:
            self.drawTriangleOnCanvas(ledge)
        redge = edge.lnext().sym()
        if redge._qedge.mark == 0:
            self.drawTriangleOnCanvas(redge)
    
    def drawTrianglesOnCanvas(self, builder, sites):
        base = builder.locateSite(sites[0])
        self.drawTriangleOnCanvas(base)
    
    def drawMapOnCanvas(self, districts, lines):
        self.w.create_rectangle(0, 0, self.width, self.height, fill=colorHex(colorMapping[DistrictType.OCEAN]))
        for district in districts:
            self.w.create_polygon(district.borders, fill=district.color_hex)
        for line in lines:
            self.w.create_line(line.line, width=line.width, fill=line.color_hex)

def main(): 
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == '__main__':
    main()
