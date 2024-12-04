import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_WaveTest import PSeq_WaveTest
import numpy as np

class PSeq_WaveTest_Blip(PSeq_WaveTest):
    
    def __init__(self, pseq=None, 
                 min_ramp = 60e-6, 
                 ramp_inc = 10e-6, 
                 *args, **kwargs):
        
        self.min_ramp = min_ramp
        self.ramp_inc = ramp_inc
        
        super().__init__(pseq, *args, **kwargs)
        
        
    def prep_waves(self):
        self.all_test_waves = []
        self.all_test_waves_neg = []
        self.all_refocus_areas = []
        for i in range(self.N_waves):
            ramp_time = self.min_ramp + i*self.ramp_inc
            amp = self.slew*ramp_time

            wave = pp.make_trapezoid(channel = self.channels[2], flat_time=0, amplitude=amp,
                                  rise_time=ramp_time, fall_time=ramp_time, 
                                  delay=self.wave_delay, system=self.system)
            self.all_test_waves.append(wave)
            
            self.all_refocus_areas.append(-wave.area)
            
            wave = pp.make_trapezoid(channel = self.channels[2], flat_time=0, amplitude=-amp,
                                  rise_time=ramp_time, fall_time=ramp_time, 
                                  delay=self.wave_delay, system=self.system)
            self.all_test_waves_neg.append(wave)