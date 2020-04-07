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
    def __init__(self, parent, data, vals):
        wx.Panel.__init__(self, parent=parent, style=wx.BORDER_RAISED, size=(100, 50))

        PCE = vals[0]
        VocL = vals[1]
        JscL = vals[2]
        FF = vals[3]
        datas = [PCE, VocL, JscL, FF]
        n_rows = len(datas)
        rows = ['$PCE\ [\%]$', '$V_{OC}\ [V]$', '$J_{SC}\ [mA/cm^2]$', '$FF\ [\%]$']
        cell_text = []
        for row in range(n_rows):
            if row != 1:
                cell_text.append(['%1.1f' % datas[row]])
            else:
                cell_text.append(['%1.2f' % datas[row]])

        zeros = np.zeros(len(data[:, 0]))

        self.figure, self.axes = plt.subplots(figsize=(4, 4))
        mpl.rc('axes', linewidth=3)
        self.axes.plot(data[:, 0], data[:, 2], linewidth=3.0)
        self.axes.plot([0, 1.3], [0, 0], color='.5', linestyle='--', linewidth=2)
        self.axes.plot(zeros, data[:, 2], c='k')
        self.axes.plot(data[:, 0], zeros, c='k')
        self.axes.set_xlabel('$Voltage\ [V]$')
        self.axes.set_ylabel('$Current\ Density\ [mA/cm^2]$')
        self.axes.set_xlim([-0.2, 0.8])
        self.axes.set_ylim([-5, 20])
        self.axes.table(cellText=cell_text, rowLabels=rows, loc='bottom', bbox=[0.3, 0.5, 0.6, 0.4])
        self.axes.tick_params(which='both', width=3, length=10)

        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.EXPAND)
        self.SetSizer(self.sizer)


class Main(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="JV Curves", size=(1300, 800))

        self.plots = [0, 0, 0, 0, 0, 0, 0, 0]
        self.vals = [0, 0, 0, 0, 0, 0, 0, 0]
        self.list_ctrl = wx.ListCtrl(self, style=wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, 'Filename')

        self.plots = self.onOpenDirectory()
        self.vals = self.calcVals(self.plots)
        # btn = wx.Button(self, label="Open Folder")
        # btn.Bind(wx.EVT_BUTTON, self.onOpenDirectory)
        btn = wx.Button(self, label="Export Values")
        btn.Bind(wx.EVT_BUTTON, self.onClick(self.vals))

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.ALL | wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL | wx.CENTER, 5)
        self.SetSizer(sizer)

        self.sp = wx.SplitterWindow(self)
        panel1 = panel(self.sp, self.plots[0], self.vals[0])
        panel2 = panel(self.sp, self.plots[1], self.vals[1])
        self.sp.SplitVertically(panel1, panel2)
        self.sp2 = wx.SplitterWindow(self)
        panel3 = panel(self.sp2, self.plots[2], self.vals[2])
        panel4 = panel(self.sp2, self.plots[3], self.vals[3])
        self.sp2.SplitVertically(panel3, panel4)
        self.sp3 = wx.SplitterWindow(self)
        panel5 = panel(self.sp3, self.plots[4], self.vals[4])
        panel6 = panel(self.sp3, self.plots[5], self.vals[5])
        self.sp3.SplitVertically(panel5, panel6)
        self.sp4 = wx.SplitterWindow(self)
        panel7 = panel(self.sp4, self.plots[6], self.vals[6])
        panel8 = panel(self.sp4, self.plots[7], self.vals[7])
        self.sp4.SplitVertically(panel7, panel8)

        sizer.Add(self.sp, 1, wx.EXPAND)
        sizer.Add(self.sp2, 1, wx.EXPAND)
        sizer.Add(self.sp3, 1, wx.EXPAND)
        sizer.Add(self.sp4, 1, wx.EXPAND)

        self.SetAutoLayout(True)
        self.Layout()

    def onClick(self, vals):
        return_text = ['PCE ', ' VocL ', ' Jsc ', ' FF ']
        total_return = []
        filename = "output"
        np.savetxt(filename, self.vals, delimiter=" ", fmt="%s", header='PCE, VocL, Jsc, FF')

    def onOpenDirectory(self):
        dlg = wx.DirDialog(self, "Choose a directory:")
        if dlg.ShowModal() == wx.ID_OK:
            self.folder_path = dlg.GetPath()
            Main.updateDisplay(self, self.folder_path)
        dlg.Destroy()
        return self.plots

    def calcVals(self, plots):
        for i in range(0, 8):
            JVinterp = interp1d(self.plots[i][:, 0], self.plots[i][:, 2], kind='cubic', bounds_error=False,
                                fill_value='extrapolate')
            JscL = -JVinterp(0)
            VocL = fsolve(JVinterp, .95 * max(self.plots[i][:, 0]))
            PPV = fmin(lambda x: x * JVinterp(x), .8 * VocL, disp=False)
            PCE = -PPV * JVinterp(PPV)
            FF = PCE / (JscL * VocL) * 100
            self.vals[i] = [PCE.item(), VocL.item(), JscL.item(), FF.item()]
        return self.vals

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

