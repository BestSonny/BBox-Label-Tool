#-------------------------------------------------------------------------------
# Name:        Truck classification and bounding box tool
# Purpose:     Mass labeling of truck classification data
# Author:      Chris-Moffitt (Based on Object bounding box label tool by Qiushi)
# Created:     06/06/2014 by Qiushi
# Modified:    02/19/2018 by Chris-Moffitt
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
import distutils.dir_util
import subprocess
import time


# colors for the bboxes
COLORS = ['red', 'blue', 'olive', 'teal', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class LabelTool():
    def __init__(self, master):
        # set up the 3 main frames
        self.parent = master
        self.parent.title("Truck Classification Tool")
        self.imageFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.imageFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.labelFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.labelFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.exampleFrame = Frame(self.parent, relief = GROOVE, bd = 1)
        self.exampleFrame.pack(side = LEFT, fill = Y, padx = 2.5, pady = 2.5)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.imgloaded = 0
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.saveImagePath = ''
        self.labelfilename = ''
        self.comfilename = ''
        self.saveLabelPath = ''
        self.deleteLabelPath= ''
        self.deleteImagePath= ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []
        self.trac_can_temp = []
        self.trail_can_temp = []
        self.trailsub_can_temp = []

        self.flatbedsub_can_temp = []
        self.tanksub_can_temp = []
        self.chassissub_can_temp = []
        self.enclosedsub_can_temp = []
        self.specialtysub_can_temp = []

        self.commodity_can_temp = []
        self.commoditysub_can_temp = []
        self.commoditysubsub_can_temp = []

        self.Raw_Materials_Agriculture_Forestry_Fishing_can_temp = []
        self.Mining_Quarrying_and_Oil_and_Gas_Extraction_can_temp = []
        self.Construction_can_temp = []
        self.Manufacturing_Production_can_temp = []
        self.Transportation_and_Other_can_temp = []
        self.Retail_Ready_Finished_Goods_can_temp = []

        self.Crops_can_temp = []
        self.Animal_Aquaculture_can_temp = []
        self.Mining_Except_Oil_Gas_can_temp = []
        self.Food_and_Beverages_can_temp = []
        self.Plant_Products_NonEdible_can_temp = []


        self.hazmatVar = StringVar()
        self.refVar = StringVar()
        self.loadVar = StringVar()
        self.classcandidate_filename = 'class.txt'
        self.tractortype_filename = 'tractortype.txt'
        self.trailertype_filename = 'trailertype.txt'
        self.trailersubtype_filename = 'trailersubtype.txt'

        self.flatbedsubtype_filename = 'flatbedsubtype.txt'
        self.tanksubtype_filename = 'tanksubtype.txt'
        self.enclosedsubtype_filename = 'enclosedsubtype.txt'
        self.chassissubtype_filename = 'chassissubtype.txt'
        self.specialtysubtype_filename = 'specialtysubtype.txt'

        self.commodity_filename = 'commodity.txt'
        self.commodity_subtype_filename = 'commodity_subtype.txt'
        self.commodity_subsubtype_filename = 'commodity_subsubtype.txt'

        self.Raw_Materials_Agriculture_Forestry_Fishing_filename = 'Raw_Materials_Agriculture_Forestry_Fishing.txt'
        self.Mining_Quarrying_and_Oil_and_Gas_Extraction_filename= 'Mining_Quarrying_and_Oil_and_Gas_Extraction.txt'
        self.Construction_filename= 'Construction.txt'
        self.Manufacturing_Production_filename= 'Manufacturing_Production.txt'
        self.Transportation_and_Other_filename= 'Transportation_and_Other.txt'
        self.Retail_Ready_Finished_Goods_filename= 'Retail_Ready_Finished_Goods.txt'

        self.Crops_filename= 'Crops.txt'
        self.Animal_Aquaculture_filename= 'Animal_Aquaculture.txt'
        self.Mining_Except_Oil_Gas_filename= 'Mining_Except_Oil_Gas.txt'
        self.Food_and_Beverages_filename= 'Food_and_Beverages.txt'
        self.Plant_Products_NonEdible_filename= 'Plant_Products_NonEdible.txt'

        self.deletedInImage=0
        self.changed=False
        self.saved=False
        self.deleted=False
        self.exampleImage = None
        self.exampleImage2 = None
        self.exampleImage3 = None

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.comList = []
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        #Create a notebook for switching between labeling and uploading
        self.nb = ttk.Notebook(self.imageFrame)
        # dir entry & load
        self.browsePanel = Frame(self.nb)
        self.label = Label(self.browsePanel, text = "Load Image Dir:")
        self.label.pack(side = LEFT)
        self.gallery = StringVar()
        self.entry = ttk.Combobox(self.browsePanel,state='readonly',textvariable=self.gallery)

        self.entry.pack(side = LEFT, ipadx = 80)

        self.galleries = [name for name in os.listdir("./Images")]
        self.entry['values'] = self.galleries
        self.LoadBtn = Button(self.browsePanel, text = "Load", command = self.LoadDir)
        self.LoadBtn.pack(side = LEFT, ipadx = 12, padx = (1,0))
        # Upload Panel
        self.uploadPanel = Frame(self.nb)
        self.uploadLabel = Label(self.uploadPanel, text = "Select Video To Classify:")
        self.uploadLabel.pack(side = LEFT)
        self.videoGallery = StringVar()
        self.uploadEntry = ttk.Combobox(self.uploadPanel,state='readonly',textvariable=self.videoGallery)
        self.uploadEntry.pack(side = LEFT, ipadx = 56)
        self.videoGalleries = [name for name in os.listdir("./Videos")]
        self.uploadEntry['values'] = self.videoGalleries
        self.uploadBtn = Button(self.uploadPanel, text = "Classify", command = self.uploadDir)
        self.uploadBtn.pack(side = LEFT, ipadx = 5)
        #Setup the notebook
        self.nb.add(self.browsePanel, text="Label")
        self.nb.add(self.uploadPanel, text="Classify")
        self.nb.pack(fill = X, padx = 1)

        #Add status panel so people know current status of images
        self.statusPanel = Frame(self.imageFrame)
        self.statusPanel.pack()
        self.statusText = Label(self.statusPanel, text='')
        self.statusText.pack(side = LEFT)
        self.status = Label(self.statusPanel, text='')
        self.status.pack(side = LEFT)

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
        self.listbox = Listbox(self.labelFrame, width = 40, height = 12, exportselection = False)
        self.listbox.pack()
        self.listbox.bind('<<ListboxSelect>>',self.selectLabel)
        self.deleteFrame = Frame(self.labelFrame)
        self.deleteFrame.pack(pady = 5)
        self.btnDel = Button(self.deleteFrame, text = 'Delete', command = self.delBBox)
        self.btnDel.pack( padx= 5, ipadx = 10, side = LEFT)
        self.btnClear = Button(self.deleteFrame, text = 'Delete All', command = self.clearBBox)
        self.btnClear.pack(padx= 5, side = LEFT)
        self.btnclass = Button(self.labelFrame, text = 'Change Selected Label', command = self.setClass)
        self.btnclass.pack(pady = (0,20), ipadx = 3)
        
        #Commodity and class tabs
        self.commodities = ttk.Notebook(self.labelFrame)
        self.commodityEditPanel = Frame(self.commodities)
        self.commodityEditPanel.pack(pady = (5,0), padx=5, fill = BOTH)

        # Choose commodity
        self.commoditynameLabel = Label(self.commodityEditPanel, text = 'Commodity')
        self.commoditynameLabel.pack(pady = (5,1))
        self.commodityname = StringVar()
        self.commoditycandidate = ttk.Combobox(self.commodityEditPanel,state='readonly',textvariable=self.commodityname)
        self.commoditycandidate.pack(fill = X, padx = 5)
        self.commoditycandidate.bind("<<ComboboxSelected>>",self.editCommoditySubtypeChoices)
        if os.path.exists(self.commodity_filename):
        	with open(self.commodity_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.commodity_can_temp.append(line.strip())

        # Choose commodity subtype
        self.subcommoditynameLabel = Label(self.commodityEditPanel, text = 'Commodity Subtype')
        self.subcommoditynameLabel.pack(pady = (5,1))
        self.subcommodityname = StringVar()
        self.subcommoditycandidate = ttk.Combobox(self.commodityEditPanel,state='readonly',textvariable=self.subcommodityname)
        self.subcommoditycandidate.pack(fill = X, padx = 5)
       	self.subcommoditycandidate.bind("<<ComboboxSelected>>",self.editCommoditySubsubtypeChoices)
        if os.path.exists(self.commodity_subtype_filename):
        	with open(self.commodity_subtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.commoditysub_can_temp.append(line.strip())
        if os.path.exists(self.Raw_Materials_Agriculture_Forestry_Fishing_filename):
        	with open(self.Raw_Materials_Agriculture_Forestry_Fishing_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Raw_Materials_Agriculture_Forestry_Fishing_can_temp.append(line.strip())
        if os.path.exists(self.Mining_Quarrying_and_Oil_and_Gas_Extraction_filename):
        	with open(self.Mining_Quarrying_and_Oil_and_Gas_Extraction_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Mining_Quarrying_and_Oil_and_Gas_Extraction_can_temp.append(line.strip())
        if os.path.exists(self.Construction_filename):
        	with open(self.Construction_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Construction_can_temp.append(line.strip())
        if os.path.exists(self.Manufacturing_Production_filename):
        	with open(self.Manufacturing_Production_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Manufacturing_Production_can_temp.append(line.strip())
        if os.path.exists(self.Transportation_and_Other_filename):
        	with open(self.Transportation_and_Other_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Transportation_and_Other_can_temp.append(line.strip())
        if os.path.exists(self.Retail_Ready_Finished_Goods_filename):
        	with open(self.Retail_Ready_Finished_Goods_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Retail_Ready_Finished_Goods_can_temp.append(line.strip())

        # Choose commodity subsubtype
        self.subsubcommoditynameLabel = Label(self.commodityEditPanel, text = 'Commodity Subsubtype')
        self.subsubcommoditynameLabel.pack(pady = (5,1))
        self.subsubcommodityname = StringVar()
        self.subsubcommoditycandidate = ttk.Combobox(self.commodityEditPanel,state='readonly',textvariable=self.subsubcommodityname)
        self.subsubcommoditycandidate.pack(fill = X, padx = 5)
        if os.path.exists(self.commodity_subsubtype_filename):
        	with open(self.commodity_subsubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.commoditysubsub_can_temp.append(line.strip())
        if os.path.exists(self.Crops_filename):
        	with open(self.Crops_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Crops_can_temp.append(line.strip())
        if os.path.exists(self.Animal_Aquaculture_filename):
        	with open(self.Animal_Aquaculture_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Animal_Aquaculture_can_temp.append(line.strip())
        if os.path.exists(self.Mining_Except_Oil_Gas_filename):
        	with open(self.Mining_Except_Oil_Gas_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Mining_Except_Oil_Gas_can_temp.append(line.strip())
        if os.path.exists(self.Food_and_Beverages_filename):
        	with open(self.Food_and_Beverages_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Food_and_Beverages_can_temp.append(line.strip())
        if os.path.exists(self.Plant_Products_NonEdible_filename):
        	with open(self.Plant_Products_NonEdible_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.Plant_Products_NonEdible_can_temp.append(line.strip())


        #Set commodity currents and values
        self.commoditycandidate['values'] = self.commodity_can_temp
        self.commoditycandidate.current(0)
        self.subcommoditycandidate['values'] = self.commoditysub_can_temp
        self.subcommoditycandidate.current(0)
        self.subsubcommoditycandidate['values'] = self.commoditysubsub_can_temp
        self.subsubcommoditycandidate.current(0)
        
        # choose class
        self.classEditPanel = Frame(self.commodities)
        self.classEditPanel.pack(pady = (5,0), padx=5, fill = BOTH)
        self.classnameLabel = Label(self.classEditPanel, text = 'Class')
        self.classnameLabel.pack(pady = (5,1))
        self.classname = StringVar()
        self.classcandidate = ttk.Combobox(self.classEditPanel,state='readonly',textvariable=self.classname)
        self.classcandidate.pack(fill = X, padx = 5)
        self.classcandidate.bind("<<ComboboxSelected>>",self.previewSelectedClass)
        if os.path.exists(self.classcandidate_filename):
        	with open(self.classcandidate_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.cla_can_temp.append(line.strip('\n'))

        # Choose a Tractor type
        self.tractornameLabel = Label(self.classEditPanel, text = 'Tractor Type')
        self.tractornameLabel.pack(pady = 1)
        self.tractorname = StringVar()
        self.tractorcandidate = ttk.Combobox(self.classEditPanel,state='readonly',textvariable=self.tractorname)
        self.tractorcandidate.pack(fill = X, padx = 5)
        if os.path.exists(self.tractortype_filename):
        	with open(self.tractortype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.trac_can_temp.append(line.strip('\n'))

        # Choose a Trailer type
        self.trailernameLabel = Label(self.classEditPanel, text = 'Trailer Type')
        self.trailernameLabel.pack(pady = 1)
        self.trailername = StringVar()
        self.trailercandidate = ttk.Combobox(self.classEditPanel,state='readonly',textvariable=self.trailername)
        self.trailercandidate.pack(fill = X, padx = 5)

        self.trailercandidate.bind("<<ComboboxSelected>>",self.editSubtypeChoices)

        if os.path.exists(self.trailertype_filename):
        	with open(self.trailertype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.trail_can_temp.append(line.strip('\n'))

        # Choose a Trailer subtype
        self.trailersubnameLabel = Label(self.classEditPanel, text = 'Trailer Subtype')
        self.trailersubnameLabel.pack(pady = 1)
        self.trailersubname = StringVar()
        self.trailersubcandidate = ttk.Combobox(self.classEditPanel,state='readonly',textvariable=self.trailersubname)
        self.trailersubcandidate.pack(fill = X, padx = 5)
        if os.path.exists(self.trailersubtype_filename):
        	with open(self.trailersubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.trailsub_can_temp.append(line.strip('\n'))

        if os.path.exists(self.flatbedsubtype_filename):
        	with open(self.flatbedsubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.flatbedsub_can_temp.append(line.strip('\n'))
        if os.path.exists(self.tanksubtype_filename):
        	with open(self.tanksubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.tanksub_can_temp.append(line.strip('\n'))
        if os.path.exists(self.enclosedsubtype_filename):
        	with open(self.enclosedsubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.enclosedsub_can_temp.append(line.strip('\n'))
        if os.path.exists(self.chassissubtype_filename):
        	with open(self.chassissubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.chassissub_can_temp.append(line.strip('\n'))
        if os.path.exists(self.specialtysubtype_filename):
        	with open(self.specialtysubtype_filename) as cf:
        		for line in cf.readlines():
        			# print line
        			self.specialtysub_can_temp.append(line.strip('\n'))

        #print self.cla_can_temp and self.truck_can_temp
        self.classcandidate['values'] = self.cla_can_temp
        self.classcandidate.current(0)
        self.tractorcandidate['values'] = self.trac_can_temp
        self.tractorcandidate.current(0)
        self.trailercandidate['values'] = self.trail_can_temp
        self.trailercandidate.current(0)
        self.trailersubcandidate['values'] = self.trailsub_can_temp
        self.trailersubcandidate.current(0)

        #Add Hazmat, refrigerant, and wide load selection
        choices = [("Yes", "Y"), ("No", "N"), ("Unknown", "U")]
        self.haz = Label(self.classEditPanel, text = 'Hazmat Truck')
        self.haz.pack(pady = 1)
        self.hazFrame = Frame(self.classEditPanel)
        self.hazFrame.pack(pady = 1)
        self.hazmatVar.set("U")
        for text, choice in choices:
            hazradiobutton = Radiobutton(self.hazFrame, text=text, variable=self.hazmatVar, value=choice)
            hazradiobutton.pack(side = LEFT)

        self.ref = Label(self.classEditPanel, text = 'Refrigerant Unit')
        self.ref.pack()
        self.refFrame = Frame(self.classEditPanel)
        self.refFrame.pack(pady = 1)
        self.refVar.set("U")
        for text, choice in choices:
            refradiobutton = Radiobutton(self.refFrame, text=text, variable=self.refVar, value=choice)
            refradiobutton.pack(side = LEFT)

        self.load = Label(self.classEditPanel, text = 'Wide load')
        self.load.pack()
        self.loadFrame = Frame(self.classEditPanel)
        self.loadFrame.pack(pady = (1,5))
        self.loadVar.set("U")
        for text, choice in choices:
            loadradiobutton = Radiobutton(self.loadFrame, text=text, variable=self.loadVar, value=choice)
            loadradiobutton.pack(side = LEFT)

        #Setup the labeling notebook
        self.commodities.add(self.classEditPanel, text="Classes")
        self.commodities.add(self.commodityEditPanel, text="Commodities")
        self.commodities.pack(fill = X, padx = 3)
        
        #Buttons to save and delete the images
        self.btnSave = Button(self.labelFrame, text = 'Save Corrected Image', command = self.saveImage)
        self.btnSave.pack( padx= 5, ipadx = 10, pady=(15,0))
        self.btnSave = Button(self.labelFrame, text = 'Delete Current Image', command = self.askDeleteQuestion)
        self.btnSave.pack( padx= 5, ipadx = 10, pady=10)

        #Help Button
        #self.btnHelp =  Button(self.labelFrame, text = 'Help', command = self.Help)
        #self.btnHelp.pack(ipadx=10, anchor = CENTER)

        #Initialize class variables
        self.currentLabelclass = self.classcandidate.get()
        self.currentTractorType = self.tractorcandidate.get()
        self.currentTrailerType = self.trailercandidate.get()
        self.currentTrailerSubType = self.trailersubcandidate.get()
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
        self.selectedImagePanel = Frame(self.egPanel, relief="groove", border = 2)
        self.selectedImagePanel.pack(pady = (15,20))
        self.classExamplePanel = Frame(self.egPanel, relief="groove", border = 2)
        self.classExamplePanel.pack(pady = (0,20))
        self.previewClassPanel = Frame(self.egPanel, relief="groove", border = 2)
        self.previewClassPanel.pack(pady =(0,0))
        self.tmpLabel2 = Label(self.selectedImagePanel, text = "Selected Box", relief="ridge", border = 5)
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.selectedImage = Canvas(self.selectedImagePanel)
        self.selectedImage.pack()
        self.selectedImage.config(width = 300, height = 150)
        self.tmpLabel3 = Label(self.classExamplePanel, text = "Label - Class", relief="ridge", border = 5)
        self.tmpLabel3.pack(side = TOP, pady = 5)
        self.classExample = Canvas(self.classExamplePanel)
        self.classExample.pack()
        self.classExample.config(width = 300, height = 150)
        self.tmpLabel4 = Label(self.previewClassPanel, text = "Dropdown - Class", relief="ridge", border = 5)
        self.tmpLabel4.pack(side = TOP, pady = 5)
        self.previewClass = Canvas(self.previewClassPanel)
        self.previewClass.pack()
        self.previewClass.config(width = 300, height = 150)

        # display mouse position
        # self.disp = Label(self.ctrPanel, text='')
        # self.disp.pack(side = LEFT)


    def uploadDir(self):
        video = self.uploadEntry.get()
        self.category = video

        subprocess.Popen('sh video_processing.sh %s'%(video), shell=True)
        time.sleep(1)
        self.galleries = [name for name in os.listdir("./Images")]
        self.entry['values'] = self.galleries


    def LoadDir(self, dbg = False):

        if not dbg:
            s = self.entry.get()
            self.parent.focus()
            self.category = s
        else:
            s = r'D:\workspace\python\labelGUI'

        # get image list
        self.imageDir = os.path.join(r'./Images', '%s' %(self.category))
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.png'))

        #print self.imageList
        if len(self.imageList) == 0:
            print 'No .png images found in the specified dir!'
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

         # set up output dir
        self.outDir = os.path.join(r'./Labels', '%s' %(self.category))
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        self.loadImage()
        print '%d images loaded from %s' %(self.total, s)

    def loadImage(self):
        # load image
        self.imgloaded = 1
        imagepath = self.imageList[self.cur - 1]
        try:
            self.img = Image.open(imagepath)
        except:
            self.deletedError()
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))
        self.deletedInImage=0
        self.statusText.config(text="Image Status:")

        # load labels and reset status variables
        self.clearBBox()
        self.saved=False
        self.changed=False
        self.deleted=False
        self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        self.notCorrected = True
        newlabelname = self.imagename + '.txt.gt'
        newcomname = self.imagename+'_com.txt.gt'

        self.saveImagePath = os.path.join(r'./Corrected/%s/Images' %(self.category),self.imagename+'.png')
        self.saveLabelPath = os.path.join(r'./Corrected/%s/Labels' %(self.category),newlabelname)
        self.saveComPath = os.path.join(r'./Corrected/%s/Labels' %(self.category),newcomname)
        self.deleteImagePath = os.path.join(r'./Deleted/%s/Images' %(self.category),self.imagename+'.png')
        self.deleteLabelPath = os.path.join(r'./Deleted/%s/Labels' %(self.category),self.imagename+'.txt')
        self.deleteComPath = os.path.join(r'./Deleted/%s/Labels' %(self.category),self.imagename+'_com.txt')
        #creat folder
        distutils.dir_util.mkpath(r'./Corrected/%s/Images' %(self.category))
        distutils.dir_util.mkpath(r'./Corrected/%s/Labels' %(self.category))
        distutils.dir_util.mkpath(r'./Deleted/%s/Images' %(self.category))
        distutils.dir_util.mkpath(r'./Deleted/%s/Labels' %(self.category))


        self.newlabelfilename = os.path.join(self.outDir, newlabelname)
        if os.path.exists(self.newlabelfilename):
            self.labelfilename = self.newlabelfilename
            self.notCorrected = False
            self.status.config(text="Corrected", fg="green4")
        else:
            labelname = self.imagename + '.txt'
            self.labelfilename = os.path.join(self.outDir, labelname)
            self.saveLabelPath = os.path.join(r'./Corrected/%s/Labels' %(self.category),labelname)
            self.status.config(text="Not Corrected", fg="red")

        self.newcomfilename = os.path.join(self.outDir, newcomname)
        if os.path.exists(self.newcomfilename):
            self.comfilename = self.newlabelfilename
        else:
            comname = self.imagename + '_com.txt'
            self.comfilename = os.path.join(self.outDir, comname)
            self.saveComPath = os.path.join(r'./Corrected/%s/Labels' %(self.category),comname)

        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
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
                    #Insert class into listbox
                    self.listbox.insert(END, 'class ---> %s    tractor ---> %s' %(tmp[4],tmp[5]))
                    self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList) - 1) % len(COLORS)])
                    if (len(self.bboxList)!=0):
                        self.listbox.select_set(0)
                        self.listbox.event_generate("<<ListboxSelect>>")

		if os.path.exists(self.comfilename):
			with open(self.comfilename) as f:
				for (i, line) in enumerate(f):
					if i == 0:
						com_cnt = int(line.strip())
						continue
					tmp = line.split()
					self.comList.append(tuple(tmp))

    def saveImage(self):
        self.saved=True
        if self.notCorrected:
            with open(self.labelfilename+".gt", 'w') as f:
                f.write('%d\n' %len(self.bboxList))
                for bbox in self.bboxList:
                    f.write(' '.join(map(str, bbox)) + '\n')
            os.system("cp "+self.imageList[self.cur - 1]+" "+self.saveImagePath)
            os.system("cp "+self.labelfilename+".gt "+self.saveLabelPath)
        else:
            with open(self.labelfilename, 'w') as f:
                f.write('%d\n' %len(self.bboxList))
                for bbox in self.bboxList:
                    f.write(' '.join(map(str, bbox)) + '\n')
            os.system("cp "+self.imageList[self.cur - 1]+" "+self.saveImagePath)
            os.system("cp "+self.labelfilename+" "+self.saveLabelPath)
        self.status.config(text="Corrected", fg="green4")
        print 'Image No. %d saved' %(self.cur)

    def deleteImage(self):
        if self.notCorrected:
            os.system("mv "+self.imageList[self.cur - 1]+" "+self.deleteImagePath)
            os.system("mv "+self.labelfilename+" "+self.deleteLabelPath)
        else:
            os.system("mv "+self.imageList[self.cur - 1]+" "+self.deleteImagePath)
            os.system("mv "+self.labelfilename+" "+self.deleteLabelPath+".gt")
        print 'Image No. %d deleted' %(self.cur)
        self.deleted=True
        del self.imageList[self.cur-1]
        self.total=self.total-1
        self.cur=self.cur-1
        if (self.cur==self.total):
            self.prevImage()
        else:
            self.nextImage()

    def mouseClick(self, event):
        if self.STATE['click'] == 0:
            self.STATE['x'], self.STATE['y'] = event.x, event.y
        else:
            self.changed=True
            self.currentLabelclass = self.classcandidate.get()
            self.currentTractorType = self.tractorcandidate.get()
            self.currentTrailerType = self.trailercandidate.get()
            self.currentTrailerSubType = self.trailersubcandidate.get()
            self.currentHaz = self.hazmatVar.get()
            self.currentRef = self.refVar.get()
            self.currentLoad = self.loadVar.get()
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2, self.currentLabelclass, self.currentTractorType, self.currentTrailerType, self.currentTrailerSubType, \
                                                    self.currentHaz, self.currentRef, self.currentLoad))
            self.bboxIdList.append(self.bboxId)
            if (y1-10>0):
                self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1-10, fill = COLORS[(len(self.bboxList)-1+self.deletedInImage) % len(COLORS)], \
                                                    text = self.currentLabelclass, font = "6")
            else:
                self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1+10, fill = COLORS[(len(self.bboxList)-1+self.deletedInImage) % len(COLORS)], \
                                                    text = self.currentLabelclass, font = "6")
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, 'class ---> %s    tractor ---> %s' %(self.currentLabelclass,self.currentTractorType))
            self.listbox.itemconfig(len(self.bboxList) - 1, fg = COLORS[(len(self.bboxList)+self.deletedInImage-1) % len(COLORS)])
            if (len(self.bboxList)!=0):
                self.listbox.selection_clear(0,"end")
            self.listbox.select_set("end")
            self.listbox.event_generate("<<ListboxSelect>>")

        self.STATE['click'] = 1 - self.STATE['click']

    def mouseMove(self, event):
        if self.imgloaded == 1:
            # self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
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
        self.changed=True
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
        self.changed=True
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.deletedInImage=0

    def Help(self):
        tkMessageBox.showinfo("About", "Truck Classification Developed By Pan He")

    def prevImage(self, event = None):
        advance=True
        if ((self.changed==True) and (self.saved==False) and (self.deleted==False)):
            advance=self.askSaveQuestion()
        if (advance==True):
            if self.cur > 1:
                self.cur -= 1
                self.loadImage()

    def nextImage(self, event = None):
        advance=True
        if ((self.changed==True) and (self.saved==False) and (self.deleted==False)):
            advance=self.askSaveQuestion()
        if (advance==True):
            if self.cur < self.total:
                self.cur += 1
                self.loadImage()

    def gotoImage(self):
        advance=True
        if ((self.changed==True) and (self.saved==False) and (self.deleted==False)):
            advance=self.askSaveQuestion()
        if (advance==True):
            idx = int(self.idxEntry.get())
            if 1 <= idx and idx <= self.total:
                self.cur = idx
                self.loadImage()

    def setClass(self):
        self.changed=True
    	self.currentLabelclass = self.classcandidate.get()
        self.currentTractorType = self.tractorcandidate.get()
        self.currentTrailerType = self.trailercandidate.get()
        self.currentTrailerSubType = self.trailersubcandidate.get()
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
        self.bboxList[idx]=(x1, y1, x2, y2, self.currentLabelclass, self.currentTractorType, self.currentTrailerType, self.currentTrailerSubType, \
                                                self.currentHaz, self.currentRef, self.currentLoad)
        if (y1-10>0):
            self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1-10, fill = COLORS[idx % len(COLORS)], \
                                                text = self.currentLabelclass, font = "6")
        else:
            self.bboxId = self.mainPanel.create_text((x1+x2)/2, y1+10, fill = COLORS[idx % len(COLORS)], \
                                                text = self.currentLabelclass, font = "6")
        self.bboxIdList[2*idx+1]=self.bboxId
        self.bboxId = None
        self.listbox.insert(idx, 'class ---> %s    tractor ---> %s' %(self.currentLabelclass,self.currentTractorType))
        self.listbox.itemconfig(idx, fg = COLORS[idx % len(COLORS)])

    def selectLabel(self, evt):
        #Check if selection is valid
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        #Display the cropped part of the image
        x1, y1, x2, y2, classtype, tractortype, trailertype, trailersubtype, hazmat, refrigerant, wideload = self.bboxList[idx]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        imagepath = self.imageList[self.cur - 1]
        cropImage = Image.open(imagepath)
        cropImage = cropImage.crop((x1, y1, x2, y2))
        cropImage.thumbnail((300,150), Image.ANTIALIAS)
        self.exampleImage = ImageTk.PhotoImage(cropImage)
        self.selectedImage.create_image(150, 75, image = self.exampleImage, anchor=CENTER)
        #Display the example of the class in the image
        selectedClass = self.bboxList[idx][4].split("-")
        selectedClass = selectedClass[0] + ".png"

        if ((selectedClass!="unknown.png") and (selectedClass!="Unknown.png")):
          imagepath = os.path.join(r'./Examples/Classes',selectedClass)
          classExampleImage = Image.open(imagepath)
          classExampleImage.thumbnail((300,150), Image.ANTIALIAS)
          self.exampleImage2 = ImageTk.PhotoImage(classExampleImage)
          self.classExample.create_image(150, 75, image = self.exampleImage2, anchor=CENTER)

        #Show All Label Data in Edit Frame
        self.classcandidate.set(classtype)
        self.tractorcandidate.set(tractortype)
        self.trailercandidate.set(trailertype)

        self.trailercandidate.event_generate("<<ComboboxSelected>>")

        self.trailersubcandidate.set(trailersubtype)
        self.hazmatVar.set(hazmat)
        self.refVar.set(refrigerant)
        self.loadVar.set(wideload)

    def previewSelectedClass(self, evt):
        #Display the example of the class in the image
        selectedClass = self.classcandidate.get().split("-")
        selectedClass = selectedClass[0] + ".png"
        imagepath = os.path.join(r'./Examples/Classes',selectedClass)
        if ((selectedClass!="unknown.png") and (selectedClass!="Unknown.png")):
          classExampleImage = Image.open(imagepath)
          classExampleImage.thumbnail((300,150), Image.ANTIALIAS)
          self.exampleImage3 = ImageTk.PhotoImage(classExampleImage)
          self.previewClass.create_image(150, 75, image = self.exampleImage3, anchor=CENTER)

    def editSubtypeChoices(self, evt):
        selectedTrailer = self.trailercandidate.get()
        if (selectedTrailer == 'Flatbed'):
            self.trailersubcandidate['values'] = self.flatbedsub_can_temp
            self.trailersubcandidate.current(0)
        elif (selectedTrailer == 'Specialty'):
            self.trailersubcandidate['values'] = self.specialtysub_can_temp
            self.trailersubcandidate.current(0)
        elif (selectedTrailer == 'Tank'):
            self.trailersubcandidate['values'] = self.tanksub_can_temp
            self.trailersubcandidate.current(0)
        elif (selectedTrailer == 'Chassis'):
            self.trailersubcandidate['values'] = self.chassissub_can_temp
            self.trailersubcandidate.current(0)
        elif (selectedTrailer == 'Enclosed'):
            self.trailersubcandidate['values'] = self.enclosedsub_can_temp
            self.trailersubcandidate.current(0)
        else:
            self.trailersubcandidate['values'] = self.trailsub_can_temp
            self.trailersubcandidate.current(0)

    def editCommoditySubtypeChoices(self, evt):
        selectedCommodity = self.commoditycandidate.get()
        if (selectedCommodity == 'Raw_Materials_Agriculture_Forestry_Fishing'):
            self.subcommoditycandidate['values'] = self.Raw_Materials_Agriculture_Forestry_Fishing_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        elif (selectedCommodity == 'Mining_Quarrying_and_Oil_and_Gas_Extraction'):
            self.subcommoditycandidate['values'] = self.Mining_Quarrying_and_Oil_and_Gas_Extraction_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        elif (selectedCommodity == 'Transportation_and_Other'):
            self.subcommoditycandidate['values'] = self.Transportation_and_Other_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        elif (selectedCommodity == 'Construction'):
            self.subcommoditycandidate['values'] = self.Construction_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        elif (selectedCommodity == 'Manufacturing_Poduction'):
            self.subcommoditycandidate['values'] = self.Manufacturing_Poduction_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        elif (selectedCommodity == 'Retail_Ready_Finished_Goods'):
            self.subcommoditycandidate['values'] = self.Retail_Ready_Finished_Goods_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")
        else:
            self.subcommoditycandidate['values'] = self.commoditysub_can_temp
            self.subcommoditycandidate.current(0)
            self.subcommoditycandidate.event_generate("<<ComboboxSelected>>")

    def editCommoditySubsubtypeChoices(self, evt):
       selectedCommoditySub = self.subcommoditycandidate.get()
       if (selectedCommoditySub == 'Crops'):
            self.subsubcommoditycandidate['values'] = self.Crops_can_temp
            self.subsubcommoditycandidate.current(0)
       elif (selectedCommoditySub == 'Animal_Aquaculture'):
            self.subsubcommoditycandidate['values'] = self.Animal_Aquaculture_can_temp
            self.subsubcommoditycandidate.current(0)
       elif (selectedCommoditySub == 'Mining_Except_Oil_Gas'):
            self.subsubcommoditycandidate['values'] = self.Mining_Except_Oil_Gas_can_temp
            self.subsubcommoditycandidate.current(0)
       elif (selectedCommoditySub == 'Food_and_Beverages'):
            self.subsubcommoditycandidate['values'] = self.Food_and_Beverages_can_temp
            self.subsubcommoditycandidate.current(0)
       elif (selectedCommoditySub == 'Plant_Products_NonEdible'):
            self.subsubcommoditycandidate['values'] = self.Plant_Products_NonEdible_can_temp
            self.subsubcommoditycandidate.current(0)
       else:
            self.subsubcommoditycandidate['values'] = self.commoditysubsub_can_temp
            self.subsubcommoditycandidate.current(0)


    def askSaveQuestion(self):
        result = tkMessageBox.askquestion("Save Changes", "Save Changes Before Continuing?", icon="warning", type="yesnocancel")
        if result == 'yes':
            self.saveImage()
            return True
        if result == 'no':
            return True
        if result == 'cancel':
            return False

    def askDeleteQuestion(self):
        result = tkMessageBox.askquestion("Delete", "Delete the Current Image?", icon="warning", type="yesno")
        if result == 'yes':
            self.deleteImage()

    def deletedError(self):
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.png'))
        self.total = len(self.imageList)
        if (self.cur>self.total):
            self.cur = self.total
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)


    def askSaveQuestion(self):
        result = tkMessageBox.askquestion("Save Changes", "Save Changes Before Continuing?", icon="warning", type="yesnocancel")
        if result == 'yes':
            self.saveImage()
            return True
        if result == 'no':
            return True
        if result == 'cancel':
            return False

    def askDeleteQuestion(self):
        result = tkMessageBox.askquestion("Delete", "Delete the Current Image?", icon="warning", type="yesno")
        if result == 'yes':
            self.deleteImage()

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.resizable(width =  False, height = False)
    root.mainloop()
