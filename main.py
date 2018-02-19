#-------------------------------------------------------------------------------
# Name:        Object bounding box label tool
# Purpose:     Label object bboxes for ImageNet Detection data
# Author:      Qiushi
# Created:     06/06/2014
#
#-------------------------------------------------------------------------------
from __future__ import division
from Tkinter import *
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
import ttk
import os
import glob
import random

# colors for the bboxes
COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the 3 main frames
        self.parent = master
        self.parent.title("LabelTool")
        self.exampleFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.exampleFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.imageFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.imageFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.labelFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.labelFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.imgloaded = 0
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.trac_can_temp = []
        self.hazmatVar = StringVar()
        self.refVar = StringVar()
        self.loadVar = StringVar()
        self.classcandidate_filename = 'class.txt'
        self.tractortype_filename = 'tractortype.txt'
        self.deletedInImage=0

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.browsePanel = Frame(self.imageFrame)
        self.browsePanel.pack()
        self.label = Label(self.browsePanel, text = "Image Dir:")
        self.label.pack(side = LEFT)
        self.gallery = StringVar()
        self.entry = ttk.Combobox(self.browsePanel,state='readonly',textvariable=self.gallery)
        self.entry.pack(side = LEFT, ipadx = 85)
        self.galleries = [name for name in os.listdir(".\Images")]
        self.entry['values'] = self.galleries
        self.LoadBtn = Button(self.browsePanel, text = "Load", command = self.LoadDir)
        self.LoadBtn.pack(side = LEFT, ipadx = 5)

        # main panel for labeling
        self.mainPanel = Canvas(self.imageFrame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelBBox)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelBBox)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.pack()

        # showing bbox info & delete bbox
        self.lb1 = Label(self.labelFrame, text = 'Bounding boxes:')
        self.lb1.pack()
        self.listbox = Listbox(self.labelFrame, width = 45, height = 12)
        self.listbox.pack()
        self.deleteFrame = Frame(self.labelFrame)
        self.deleteFrame.pack(pady = 5)
        self.btnDel = Button(self.deleteFrame, text = 'Delete', command = self.delBBox)
        self.btnDel.pack( padx= 5, ipadx = 10, side = LEFT)
        self.btnClear = Button(self.deleteFrame, text = 'Delete All', command = self.clearBBox)
        self.btnClear.pack(padx= 5, side = LEFT)
        self.btnclass = Button(self.labelFrame, text = 'Change Selected Label', command = self.setClass)
        self.btnclass.pack(pady = (0,15), ipadx = 3)

        # choose class
        self.classnameLabel = Label(self.labelFrame, text = 'Choose Class from Dropdown:')
        self.classnameLabel.pack(pady = 1)
        self.classname = StringVar()
        self.classcandidate = ttk.Combobox(self.labelFrame,state='readonly',textvariable=self.classname)
        self.classcandidate.pack(fill = X)
        if os.path.exists(self.classcandidate_filename):
        	with open(self.classcandidate_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.cla_can_temp.append(line.strip('\n'))

        # Choose a Tractor type
        self.tractornameLabel = Label(self.labelFrame, text = 'Choose Tractor Type from Dropdown:')
        self.tractornameLabel.pack(pady = 1)
        self.tractorname = StringVar()
        self.tractorcandidate = ttk.Combobox(self.labelFrame,state='readonly',textvariable=self.tractorname)
        self.tractorcandidate.pack(fill = X)
        if os.path.exists(self.tractortype_filename):
        	with open(self.tractortype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.trac_can_temp.append(line.strip('\n'))

        #print self.cla_can_temp and self.truck_can_temp
        self.classcandidate['values'] = self.cla_can_temp
        self.classcandidate.current(0)
        self.tractorcandidate['values'] = self.trac_can_temp
        self.tractorcandidate.current(0)

        #Add Hazmat, refrigerant, and wide load selection
        choices = [("Yes", "Y"), ("No", "N"), ("Unknown", "U")]
        self.haz = Label(self.labelFrame, text = 'Hazmat Truck')
        self.haz.pack(pady = 1)
        self.hazFrame = Frame(self.labelFrame)
        self.hazFrame.pack(pady = 1)
        self.hazmatVar.set("U")
        for text, choice in choices:
            hazradiobutton = Radiobutton(self.hazFrame, text=text, variable=self.hazmatVar, value=choice)
            hazradiobutton.pack(side = LEFT)

        self.ref = Label(self.labelFrame, text = 'Refrigerant Unit')
        self.ref.pack()
        self.refFrame = Frame(self.labelFrame)
        self.refFrame.pack(pady = 1)
        self.refVar.set("U")
        for text, choice in choices:
            refradiobutton = Radiobutton(self.refFrame, text=text, variable=self.refVar, value=choice)
            refradiobutton.pack(side = LEFT)

        self.load = Label(self.labelFrame, text = 'Wide load')
        self.load.pack()
        self.loadFrame = Frame(self.labelFrame)
        self.loadFrame.pack(pady = 1)
        self.loadVar.set("U")
        for text, choice in choices:
            loadradiobutton = Radiobutton(self.loadFrame, text=text, variable=self.loadVar, value=choice)
            loadradiobutton.pack(side = LEFT)

        #Initialize class variables and add help button
        self.btnHelp =  Button(self.labelFrame, text = 'Help', command = self.Help)
        self.btnHelp.pack(ipadx=10, anchor = CENTER)
        self.currentLabelclass = self.classcandidate.get()
        self.currentTractorType = self.tractorcandidate.get()
        self.currentHaz = self.hazmatVar.get()
        self.currentRef = self.refVar.get()
        self.currentLoad = self.loadVar.get()

        # control panel for image navigation
        self.ctrPanel = Frame(self.imageFrame)
        self.ctrPanel.pack()
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)


        # example pannel for illustration
        self.egPanel = Frame(self.exampleFrame, border = 10)
        self.egPanel.pack()
        self.tmpLabel2 = Label(self.egPanel, text = "Examples:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = LEFT)

        # for debugging
##        self.setImage()
##        self.LoadDir()

    def LoadDir(self, dbg = False):
        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = int(s)
        else:
            s = r'D:\workspace\python\labelGUI'
##        if not os.path.isdir(s):
##            tkMessageBox.showerror("Error!", message = "The specified dir doesn't exist!")
##            return
        # get image list
        self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        #print self.imageDir
        #print self.category
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.png'))
        #print self.imageList
        if len(self.imageList) == 0:
            print 'No .png images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        # load example bboxes
        #self.egDir = os.path.join(r'./Examples', '%03d' %(self.category))
        self.egDir = os.path.join(r'./Examples/demo')
        print os.path.exists(self.egDir)
        if not os.path.exists(self.egDir):
            return
        filelist = glob.glob(os.path.join(self.egDir, '*.jpg'))
        self.tmp = []
        self.egList = []
        random.shuffle(filelist)
        for (i, f) in enumerate(filelist):
            if i == 3:
                break
            im = Image.open(f)
            r = min(SIZE[0] / im.size[0], SIZE[1] / im.size[1])
            new_size = int(r * im.size[0]), int(r * im.size[1])
            self.tmp.append(im.resize(new_size, Image.ANTIALIAS))
            self.egList.append(ImageTk.PhotoImage(self.tmp[-1]))
            self.egLabels[i].config(image = self.egList[-1], width = SIZE[0], height = SIZE[1])

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)

    def loadImage(self):
        # load image
        self.imgloaded = 1
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))
        self.deletedInImage=0

        # load labels
        self.clearBBox()
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        self.notCorrected = True
        newlabelname = self.imagename + '.txt.gt'
        self.newlabelfilename = os.path.join(self.outDir, newlabelname)
        if os.path.exists(self.newlabelfilename):
            self.labelfilename = self.newlabelfilename
            self.notCorrected = False
        else:
            labelname = self.imagename + '.txt'
            self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    # tmp = [int(t.strip()) for t in line.split()]
                    tmp = line.split()
                    #Draw rectangle and class name in the image
                    self.bboxList.append(tuple(tmp))
                    tmpId = self.mainPanel.create_rectangle(int(tmp[0]), int(tmp[1]), \
                                                            int(tmp[2]), int(tmp[3]), \
                                                            width = 2, \
                                                            outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    if (int(tmp[1])-10>0):
                        tmpId = self.mainPanel.create_text((int(tmp[0])+int(tmp[2]))/2, int(tmp[1])-10, fill = COLORS[(len(self.bboxList)-1) % len(COLORS)], \
                                                            text = tmp[4], font = "6")
                    else:
                        tmpId = self.mainPanel.create_text((int(tmp[0])+int(tmp[2]))/2, int(tmp[1])+10, fill = COLORS[(len(self.bboxList)-1) % len(COLORS)], \
                                                            text = tmp[4], font = "6")
                    self.bboxIdList.append(tmpId)
                    #Insert class into listbo
                    self.listbox.insert(END, '%s-%s, H : %s, R : %s, W : %s' %(tmp[4],tmp[5],tmp[6],tmp[7],tmp[8]))
                    self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList) - 1) % len(COLORS)])

    def saveImage(self):
        if self.notCorrected:
            with open(self.labelfilename+".gt", 'w') as f:
                f.write('%d\n' %len(self.bboxList))
                for bbox in self.bboxList:
                    f.write(' '.join(map(str, bbox)) + '\n')
            print 'Image No. %d saved' %(self.cur)
        else:
            with open(self.labelfilename, 'w') as f:
                f.write('%d\n' %len(self.bboxList))
                for bbox in self.bboxList:
                    f.write(' '.join(map(str, bbox)) + '\n')
            print 'Image No. %d saved' %(self.cur)


    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            self.currentLabelclass = self.classcandidate.get()
            self.currentTractorType = self.tractorcandidate.get()
            self.currentHaz = self.hazmatVar.get()
            self.currentRef = self.refVar.get()
            self.currentLoad = self.loadVar.get()
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2, self.currentLabelclass, self.currentTractorType, self.currentHaz, self.currentRef, self.currentLoad))
            self.bboxIdList.append(self.bboxId)
            if (y1-10>0):
                self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1-10, fill = COLORS[(len(self.bboxList)-1+self.deletedInImage) % len(COLORS)], \
                                                    text = self.currentLabelclass, font = "6")
            else:
                self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1+10, fill = COLORS[(len(self.bboxList)-1+self.deletedInImage) % len(COLORS)], \
                                                    text = self.currentLabelclass, font = "6")
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '%s-%s, H : %s, R : %s, W : %s' %(self.currentLabelclass,self.currentTractorType,self.currentHaz,self.currentRef, \
                                                            self.currentLoad))
            self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList)+self.deletedInImage-1) % len(COLORS)])

        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        if self.imgloaded == 1:
            self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
            if self.tkimg:
                if self.hl:
                    self.mainPanel.delete(self.hl)
                self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
                if self.vl:
                    self.mainPanel.delete(self.vl)
                self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
            if 1 == self.STATE['click']:
                if self.bboxId:
                    self.mainPanel.delete(self.bboxId)
                self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                                event.x, event.y, \
                                                                width = 2, \
                                                                outline = COLORS[(len(self.bboxList)+self.deletedInImage) % len(COLORS)])

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = 0

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[2*idx])
        self.mainPanel.delete(self.bboxIdList[2*idx+1])
        self.bboxIdList.pop(2*idx+1)
        self.bboxIdList.pop(2*idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.deletedInImage=self.deletedInImage+1

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.deletedInImage=0

    def Help(self):
        tkMessageBox.showinfo("About", "Truck Classification Developed By Pan He")

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()

    def setClass(self):
    	self.currentLabelclass = self.classcandidate.get()
        self.currentTractorType = self.tractorcandidate.get()
        self.currentHaz = self.hazmatVar.get()
        self.currentRef = self.refVar.get()
        self.currentLoad = self.loadVar.get()
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        x1, y1, x2, y2 = self.bboxList[idx][:4]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        self.mainPanel.delete(self.bboxIdList[2*idx+1])
        self.listbox.delete(idx)
        self.bboxList[idx]=(x1, y1, x2, y2, self.currentLabelclass, self.currentTractorType, self.currentHaz, self.currentRef, self.currentLoad)
        if (y1-10>0):
            self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1-10, fill = COLORS[idx % len(COLORS)], \
                                                text = self.currentLabelclass, font = "6")
        else:
            self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1+10, fill = COLORS[idx % len(COLORS)], \
                                                text = self.currentLabelclass, font = "6")
        self.bboxIdList[2*idx+1]=self.bboxId
        self.bboxId = None
        self.listbox.insert(idx, '%s-%s, H : %s, R : %s, W : %s' %(self.currentLabelclass,self.currentTractorType,self.currentHaz,self.currentRef, \
                                                        self.currentLoad))
        self.listbox.itemconfig(idx, fg = COLORS[idx % len(COLORS)])

##    def setImage(self, imagepath = r'test2.png'):
##        self.img = Image.open(imagepath)
##        self.tkimg = ImageTk.PhotoImage(self.img)
##        self.mainPanel.config(width = self.tkimg.width())
##        self.mainPanel.config(height = self.tkimg.height())
##        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  True, height = True)
    root.mainloop()
