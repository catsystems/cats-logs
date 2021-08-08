import pandas as pd
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import pyqtgraph as pg
import numpy as np
import sys
import time

def line_from_origin(row, col, type):
    return np.array(((0, 0, 0), (row[f'n{col}0_{type}'], row[f'n{col}1_{type}'], row[f'n{col}2_{type}'])))

class Visualizer(object):
    def __init__(self, df):
        self.traces = dict()
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.opts['distance'] = 50
        self.w.setWindowTitle('pyqtgraph example: GLLinePlotItem')
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()

        # create the background grids
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.w.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.w.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.w.addItem(gz)

        self.idx = 0
        self.df = df

        curr_row = self.df.iloc[self.idx]

        pts0 = line_from_origin(curr_row, 'x', 'est')
        pts1 = line_from_origin(curr_row, 'y', 'est')
        pts2 = line_from_origin(curr_row, 'z', 'est')
        pts3 = line_from_origin(curr_row, 'x', 'raw')
        pts4 = line_from_origin(curr_row, 'y', 'raw')
        pts5 = line_from_origin(curr_row, 'z', 'raw')

        self.traces[0] = gl.GLLinePlotItem(pos=pts0, color=pg.glColor(127, 127, 0), width=10, antialias=True)
        self.traces[1] = gl.GLLinePlotItem(pos=pts1, color=pg.glColor(0, 127, 127), width=10, antialias=True)
        self.traces[2] = gl.GLLinePlotItem(pos=pts2, color=pg.glColor(127, 0, 127), width=10, antialias=True)
        self.traces[3] = gl.GLLinePlotItem(pos=pts3, color=pg.glColor(255, 0, 0), width=5, antialias=True)
        self.traces[4] = gl.GLLinePlotItem(pos=pts4, color=pg.glColor(0, 255, 0), width=5, antialias=True)
        self.traces[5] = gl.GLLinePlotItem(pos=pts5, color=pg.glColor(0, 0, 255), width=5, antialias=True)

        self.w.addItem(self.traces[0])
        self.w.addItem(self.traces[1])
        self.w.addItem(self.traces[2])
        self.w.addItem(self.traces[3])
        self.w.addItem(self.traces[4])
        self.w.addItem(self.traces[5])

        self.traces[6] = gl.GLTextItem(pos=(0, 0, 12), color=(255, 255, 255, 255), text=f'Frame {self.idx}')
        self.w.addItem(self.traces[6])

        self.idx += 1

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def set_plotdata(self, name, points, color, width):
        self.traces[name].setData(pos=points, color=color, width=width)

    def update(self):
        # start_time = time.time()
        if self.idx < len(self.df):
            curr_row = self.df.iloc[self.idx]
            pts0 = line_from_origin(curr_row, 'x', 'est')
            pts1 = line_from_origin(curr_row, 'y', 'est')
            pts2 = line_from_origin(curr_row, 'z', 'est')
            pts3 = line_from_origin(curr_row, 'x', 'raw')
            pts4 = line_from_origin(curr_row, 'y', 'raw')
            pts5 = line_from_origin(curr_row, 'z', 'raw')

            self.set_plotdata(name=0, points=pts0, color=pg.glColor(127, 127, 0), width=10)
            self.set_plotdata(name=1, points=pts1, color=pg.glColor(0, 127, 127), width=10)
            self.set_plotdata(name=2, points=pts2, color=pg.glColor(127, 0, 127), width=10)

            self.set_plotdata(name=3, points=pts3, color=pg.glColor(255, 0, 0), width=5)
            self.set_plotdata(name=4, points=pts4, color=pg.glColor(0, 255, 0), width=5)
            self.set_plotdata(name=5, points=pts5, color=pg.glColor(0, 0, 255), width=5)

            self.idx += 1

            self.traces[6].setData(pos=(0, 0, 12), color=(255, 255, 255, 255),
                                   text=f"Time: {curr_row['ts']} s")
        else:
            self.idx = 0
        # end_time = time.time()
        #
        # print(end_time - start_time)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()


def quat_mult(q, p):
    Q_mat = np.array([[q[0], -q[1], -q[2], -q[3]], [q[1], q[0], -q[3], q[2]], [q[2], q[3], q[0], -q[1]],
                      [q[3], -q[2], q[1], q[0]]])
    return np.squeeze(np.matmul(Q_mat, p))


def conj_q(q):
    return np.array([q[0], -q[1], -q[2], -q[3]])


# Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    q_df = pd.read_csv('../log_parsing/output/teraterm/processed/teraterm - orientation_info_processed.csv',
                       index_col=0)

    ex = np.array([0, 1, 0, 0])
    ey = np.array([0, 0, 1, 0])
    ez = np.array([0, 0, 0, 1])

    q_est = np.array([q_df['q0_estimated'], q_df['q1_estimated'], q_df['q2_estimated'], q_df['q3_estimated']])
    q_raw = np.array([q_df['q0_raw'], q_df['q1_raw'], q_df['q2_raw'], q_df['q3_raw']])
    size_df = np.shape(q_est)
    coord_sys = []
    for index in range(0, size_df[1]):
        quatx = quat_mult(quat_mult(conj_q(q_est[:, index]), ex), q_est[:, index])
        quaty = quat_mult(quat_mult(conj_q(q_est[:, index]), ey), q_est[:, index])
        quatz = quat_mult(quat_mult(conj_q(q_est[:, index]), ez), q_est[:, index])
        quatx_raw = quat_mult(quat_mult(conj_q(q_raw[:, index]), ex), q_raw[:, index])
        quaty_raw = quat_mult(quat_mult(conj_q(q_raw[:, index]), ey), q_raw[:, index])
        quatz_raw = quat_mult(quat_mult(conj_q(q_raw[:, index]), ez), q_raw[:, index])
        coord_sys.append({'ts': q_df['ts'][index],
                          'nx0_est': quatx[1],
                          'nx1_est': quatx[2],
                          'nx2_est': quatx[3],
                          'ny0_est': quaty[1],
                          'ny1_est': quaty[2],
                          'ny2_est': quaty[3],
                          'nz0_est': quatz[1],
                          'nz1_est': quatz[2],
                          'nz2_est': quatz[3],
                          'nx0_raw': quatx_raw[1],
                          'nx1_raw': quatx_raw[2],
                          'nx2_raw': quatx_raw[3],
                          'ny0_raw': quaty_raw[1],
                          'ny1_raw': quaty_raw[2],
                          'ny2_raw': quaty_raw[3],
                          'nz0_raw': quatz_raw[1],
                          'nz1_raw': quatz_raw[2],
                          'nz2_raw': quatz_raw[3]})

    coord_sys_df = pd.DataFrame(coord_sys)

    for column in coord_sys_df:
        if column != 'ts':
            if 'raw' in column:
                coord_sys_df[column] /= 7
            else:
                coord_sys_df[column] /= 10

    v = Visualizer(coord_sys_df)
    v.animation()