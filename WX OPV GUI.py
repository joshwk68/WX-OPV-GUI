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

class panel(wx.Panel):
    def __init__(self, parent, data):
        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_RAISED, size=(350, 50))
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.axes.plot(data)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


def calculate_values(data):
    Ldata = dataframe(data)
    JVinterp = interp1d(Ldata[:, 0], Ldata[:, 2], kind='cubic', bounds_error=False, fill_value='extrapolate')
    JscL = -JVinterp(0)
    VocL = fsolve(JVinterp, .95 * max(Ldata[:, 0]))
    PPV = fmin(lambda x: x * JVinterp(x), .8 * VocL, disp=False)
    PCE = -PPV * JVinterp(PPV)
    FF = PCE / (JscL * VocL) * 100
    return PCE, VocL, JscL, FF

class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="JV Curves", size=(1200, 1200))

        self.plots = [0,0,0,0,0,0,0,0]
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

        self.sp = wx.SplitterWindow(self)
        panel1 = panel(self.sp, self.plots[0])
        panel2 = panel(self.sp, self.plots[1])
        self.sp.SplitVertically(panel1, panel2)
        self.sp2 = wx.SplitterWindow(self)
        panel3 = panel(self.sp2, self.plots[2])
        panel4 = panel(self.sp2, self.plots[3])
        self.sp2.SplitVertically(panel3, panel4)
        self.sp3 = wx.SplitterWindow(self)
        panel5 = panel(self.sp3, self.plots[4])
        panel6 = panel(self.sp3, self.plots[5])
        self.sp3.SplitVertically(panel5, panel6)
        self.sp4 = wx.SplitterWindow(self)
        panel7 = panel(self.sp4, self.plots[6])
        panel8 = panel(self.sp4, self.plots[7])
        self.sp4.SplitVertically(panel7, panel8)

        sizer.Add(self.sp, 1, wx.EXPAND)
        sizer.Add(self.sp2, 1, wx.EXPAND)
        sizer.Add(self.sp3, 1, wx.EXPAND)
        sizer.Add(self.sp4, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.Layout()

    def onOpenDirectory(self, event):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            Main.updateDisplay(self, path)
        dlg.Destroy()

    def updateDisplay(self, folder_path):
        paths = glob.glob(folder_path + "/*.liv1*")
        for i in range(0,8):
            self.plots[i] = np.loadtxt(paths[i], delimiter = '\t', max_rows=34)
            self.plots[i] = self.plots[i] * -1
        for index, path in enumerate(paths):
            self.list_ctrl.InsertStringItem(index, os.path.basename(path))
        return self.plots


app = wx.App(redirect=False)
frame = Main()
frame.Show()
app.MainLoop()

