import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_Base import Pseq_Base
import numpy as np

class PSeq_Refocus_PE(Pseq_Base):
    def __init__(self, pseq=None, 
                 areas0 = None,
                 areas1 = None,
                 areas2 = None,
                 *args, **kwargs):
        
        super().__init__(pseq, *args, **kwargs)
        
        self.areas0 = areas0
        self.areas1 = areas1
        self.areas2 = areas2
        
        max_area = 0
        if areas0 is not None:
            max_area = max(max_area, max(np.abs(areas0)))
        if areas1 is not None:
            max_area = max(max_area, max(np.abs(areas1)))
        if areas2 is not None:
            max_area = max(max_area, max(np.abs(areas2)))
        
        # print(f'{max_area = }')
        self.max_area = max_area

        max_grad = pp.make_trapezoid(channel = 'x', area=max_area, system = self.system)
        self.duration = pp.calc_duration(max_grad)
        
        # print(f'{self.duration = }')

    
    def make_default_seq(self, ie0=0, ie1=0, ie2=0, polarity2 = 1):
        self.init_seq()
        
        blocks_to_play = []
        if self.areas0 is not None:
            grad0 = pp.make_trapezoid(channel = self.channels[0], area=self.areas0[ie0], duration = self.duration, system = self.system)
            blocks_to_play.append(grad0)
        if self.areas1 is not None:
            grad1 = pp.make_trapezoid(channel = self.channels[1], area=self.areas1[ie1], duration = self.duration, system = self.system)
            blocks_to_play.append(grad1)
        if self.areas2 is not None:
            grad2 = pp.make_trapezoid(channel = self.channels[2], area=polarity2*self.areas2[ie2], duration = self.duration, system = self.system)
            blocks_to_play.append(grad2)
        
        self.seq.add_block(*blocks_to_play)

    def add_to_seq(self, pseq0, ie0=0, ie1=0, ie2=0, polarity2 = 1):
        blocks_to_play = []
        if self.areas0 is not None:
            grad0 = pp.make_trapezoid(channel = pseq0.channels[0], area=self.areas0[ie0], duration = self.duration, system = self.system)
            blocks_to_play.append(grad0)
        if self.areas1 is not None:
            grad1 = pp.make_trapezoid(channel = pseq0.channels[1], area=self.areas1[ie1], duration = self.duration, system = self.system)
            blocks_to_play.append(grad1)
        if self.areas2 is not None:
            grad2 = pp.make_trapezoid(channel = pseq0.channels[2], area=polarity2*self.areas2[ie2], duration = self.duration, system = self.system)
            blocks_to_play.append(grad2)
        
        pseq0.seq.add_block(*blocks_to_play)
        pseq0.track_time = pseq0.track_time + pp.calc_duration(*blocks_to_play)
            

    def get_duration(self, ie0=0, ie1=0, ie2=0, polarity2 = 1):
        blocks_to_play = []
        if self.areas0 is not None:
            grad0 = pp.make_trapezoid(channel = self.channels[0], area=self.areas0[ie0], duration = self.duration, system = self.system)
            blocks_to_play.append(grad0)
        if self.areas1 is not None:
            grad1 = pp.make_trapezoid(channel = self.channels[1], area=self.areas1[ie1], duration = self.duration, system = self.system)
            blocks_to_play.append(grad1)
        if self.areas2 is not None:
            grad2 = pp.make_trapezoid(channel = self.channels[2], area=polarity2*self.areas2[ie2], duration = self.duration, system = self.system)
            blocks_to_play.append(grad2)
        
        dur = pp.calc_duration(*blocks_to_play)
        return dur