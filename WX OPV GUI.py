import matplotlib
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import wx
import glob
import os
import wx
import wx.lib.agw.multidirdialog as MDD
import numpy as np
import pandas as pd
import math
from scipy.optimize import fsolve
from scipy.optimize import fmin
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os
from os import listdir
import base64
import datetime
import io
from textwrap import dedent as d
from scipy import stats
from decimal import Decimal
import plotly.graph_objs as go

plots = [None] * 8
perf = [None] * 8

class topPanel(wx.Panel):
    def __init__(self, parent):
        super(topPanel, self).__init__(parent)

        self.list_ctrl = wx.ListCtrl(self,
                                     style=wx.LC_REPORT
                                           | wx.BORDER_SUNKEN
                                     )
        self.list_ctrl.InsertColumn(0, 'Filename')

        btn = wx.Button(self, label="Open Folder")
        btn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(sizer)

    def onOpenDirectory(self, event):
        """"""
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.updateDisplay(path)
        dlg.Destroy()

    # ----------------------------------------------------------------------
    def updateDisplay(self, folder_path):
        """
        Update the listctrl with the file names in the passed in folder
        """
        paths = glob.glob(folder_path + "/*.liv1*")
        for index, path in enumerate(paths):
            self.list_ctrl.InsertStringItem(index, os.path.basename(path))

# def collect_data(paths):
#     for i in paths:
#         plots[i] = dataframe(paths[i])
#         perf[i] = get_values(plots[i])
#     return plots, perf
#
#
# def dataframe(data):
#     Ldata = data
#     idx_end = Ldata[Ldata.iloc[:, 0] == 'Jsc:'].index[0]
#     Ldata = Ldata.iloc[:idx_end - 1, :]
#     Ldata.iloc[:, 0] = pd.to_numeric(Ldata.iloc[:, 0])
#     Ldata.iloc[:, 0]
#     Ldata = np.array(Ldata)
#     Ldata = np.insert(Ldata, 2, -Ldata[:, 1], axis=1)
#     return Ldata
#
# def get_values(data):
#     values = calculate_values(data)
#     PCE = values[0]
#     VocL = values[1]
#     JscL = values[2]
#     FF = values[3]
#     return PCE, VocL, JscL, FF
#
# def calculate_values(data):
#     Ldata = dataframe(data)
#     JVinterp = interp1d(Ldata[:, 0], Ldata[:, 2], kind='cubic', bounds_error=False, fill_value='extrapolate')
#     JscL = -JVinterp(0)
#     VocL = fsolve(JVinterp, .95 * max(Ldata[:, 0]))
#     PPV = fmin(lambda x: x * JVinterp(x), .8 * VocL, disp=False)
#     PCE = -PPV * JVinterp(PPV)
#     FF = PCE / (JscL * VocL) * 100
#     datas = [PCE, VocL, JscL, FF]
#     return datas

class panel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self,parent=parent, style = wx.BORDER_RAISED, size=(350,50))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.plot(0,0)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="JV Curves", size=(1200, 1200))

        topBar = topPanel(self)
        self.sp = wx.SplitterWindow(self)
        panel1 = panel(self.sp)
        panel2 = panel(self.sp)
        self.sp.SplitVertically(panel1, panel2)
        self.sp2 = wx.SplitterWindow(self)
        panel3 = panel(self.sp2)
        panel4 = panel(self.sp2)
        self.sp2.SplitVertically(panel3, panel4)
        self.sp3 = wx.SplitterWindow(self)
        panel5 = panel(self.sp3)
        panel6 = panel(self.sp3)
        self.sp3.SplitVertically(panel5, panel6)
        self.sp4 = wx.SplitterWindow(self)
        panel7 = panel(self.sp4)
        panel8 = panel(self.sp4)
        self.sp4.SplitVertically(panel7, panel8)

        panel1.SetBackgroundColour("BLUE")
        panel2.SetBackgroundColour("RED")
        panel3.SetBackgroundColour("BLUE")
        panel4.SetBackgroundColour("RED")
        panel5.SetBackgroundColour("BLUE")
        panel6.SetBackgroundColour("RED")
        panel7.SetBackgroundColour("BLUE")
        panel8.SetBackgroundColour("RED")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topBar, 1, wx.EXPAND)
        sizer.Add(self.sp, 1, wx.EXPAND)
        sizer.Add(self.sp2, 1, wx.EXPAND)
        sizer.Add(self.sp3, 1, wx.EXPAND)
        sizer.Add(self.sp4, 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Layout()

app = wx.App(redirect=False)
frame = Main()
frame.Show()
app.MainLoop()

