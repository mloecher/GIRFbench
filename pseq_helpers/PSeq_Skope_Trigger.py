import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_Base import Pseq_Base
import numpy as np

class PSeq_Skope_Trigger(Pseq_Base):
    
    def __init__(self, pseq=None, 
                 duration = 40e-6,
                 *args, **kwargs):
        
        super().__init__(pseq, *args, **kwargs)
        
        self.duration = duration
        self.trig = pp.make_digital_output_pulse(channel='ext1', duration=self.system.grad_raster_time)
        self.pp_delay = pp.make_delay(self.duration)
        
    def make_default_seq(self, i_pe0 = 0, i_pe1 = 0):
        
        self.init_seq()
        self.seq.add_block(self.trig, self.pp_delay)
        

    def add_to_seq(self, pseq0, i_pe0 = 0, i_pe1 = 0, offset=0):
        pseq0.seq.add_block(self.trig, self.pp_delay)
        pseq0.track_time = pseq0.track_time + pp.calc_duration(self.trig, self.pp_delay)

    def get_duration(self):
        dur = pp.calc_duration(self.trig, self.pp_delay)
        return dur
    
    def get_duration_from_excite(self):
        dur = pp.calc_duration(self.trig, self.pp_delay) - pp.calc_duration(self.trig)
        return dur