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
        JVinterp = interp1d(data[:, 0], data[:, 2], kind='cubic', bounds_error=False, fill_value='extrapolate')
        JscL = -JVinterp(0)
        VocL = fsolve(JVinterp, .95*max(data[:, 0]))
        PPV = fmin(lambda x: x*JVinterp(x), .8 * VocL, disp=False)
        PCE = -PPV * JVinterp(PPV)
        FF = PCE / (JscL * VocL) * 100
        datas = [PCE, VocL, JscL, FF]
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111, xlabel='$Voltage\ [V]$', ylabel='$Current\ Density\ [mA/cm^2]$', ylim=(-20, 5), xlim=(0, 1.3))
        default_figsize = mpl.rcParamsDefault['figure.figsize']
        mpl.rcParams['figure.figsize'] = [1.5 * val for val in default_figsize]
        font = {'family': 'DejaVu Sans',
                'weight': 'bold',
                'size': 22}

        mpl.rc('font', **font)
        mpl.rc('axes', linewidth=3)

        datas = [PCE, VocL, JscL, FF]
        n_rows = len(datas)
        rows = ['$PCE\ [\%]$', '$V_{OC}\ [V]$', '$J_{SC}\ [mA/cm^2]$', '$FF\ [\%]$']
        cell_text = []
        for row in range(n_rows):
            if row != 1:
                cell_text.append(['%1.1f' % datas[row]])
            else:
                cell_text.append(['%1.2f' % datas[row]])

        self.axes.plot(data[:, 0], data[:, 2], linewidth=3.0)
        self.axes.plot([0, 1.3], [0, 0], color='.5', linestyle='--', linewidth=2)
        self.axes.table(cellText=cell_text, rowLabels=rows, loc='bottom', bbox=[0.45, 0.5, 0.15, 0.4])
        self.axes.tick_params(which='both', width=3, length=10)
        # plt.figure(figsize=(300, 250), dpi= 80, facecolor='w', edgecolor='k')
        # self.axes.plot(data[:,0], data[:,2])
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="JV Curves", size=(1200, 1200))

        self.plots = [0,0,0,0,0,0,0,0]
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Filename')

        # btn = wx.Button(self, label="Open Folder")
        # btn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        self.plots = self.onOpenDirectory()

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        # sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)
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
        self.scroll = wx.lib.scrolledpanel.ScrolledPanel(self, -1, size=(screenWidth, 400), pos=(0, 28),
                                                    style=wx.SIMPLE_BORDER)
        self.SetupScrolling()
        self.SetAutoLayout(True)
        self.Layout()

    def onOpenDirectory(self):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_path = dlg.GetPath()
            Main.updateDisplay(self, self.folder_path)
        dlg.Destroy()
        return self.plots


    def updateDisplay(self, folder_path):
        paths = glob.glob(self.folder_path + "/*.liv1")
        for i in range(0, 8):

            self.plots[i] = pd.read_csv(paths[i], delimiter='\t', header=None)
            idx_end = self.plots[i][self.plots[i].iloc[:, 0] == 'Jsc:'].index[0]
            self.plots[i] = self.plots[i].iloc[:idx_end - 1, :]
            self.plots[i].iloc[:, 0] = pd.to_numeric(self.plots[i].iloc[:, 0])
            self.plots[i] = np.array(self.plots[i])
            self.plots[i] = np.insert(self.plots[i], 2, -self.plots[i][:, 1], axis=1)

            # self.plots[i] = np.loadtxt(paths[i], delimiter='\t',
            #                            max_rows=34)
            # self.plots[i] = self.plots[i] * -1
        for index, pth in enumerate(paths):
            self.list_ctrl.InsertItem(index, os.path.basename(pth))
        return self.folder_path

app = wx.App(redirect=False)
frame = Main()
frame.Show()
app.MainLoop()

