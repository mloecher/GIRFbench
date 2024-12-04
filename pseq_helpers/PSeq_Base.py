import numpy as np
import pypulseq as pp
from pypulseq.opts import Opts

class Pseq_Base:
    def __init__(self, pseq=None, channels=("x","y","z"), rf_spoil = True, **kwargs):
        
        if pseq is not None:
            self.system = pseq.system
            self.channels = pseq.channels
            self.rf_spoil = pseq.rf_spoil
        else:
            # Some defaults for my use cases
            opt_args = {"grad_unit": "mT/m", 
                        "slew_unit": "T/m/s",
                        "rf_ringdown_time": 30e-6,
                        "rf_dead_time": 100e-6,
                        "adc_dead_time": 10e-6,
                        "B0":  2.89,
                        "adc_samples_limit":8192,
                        }
            
            # Add any Opts arguments from kwargs to the self Opts
            for key, val in kwargs.items():
                if key in Opts.default.__dict__:
                    opt_args[key] = val
                    
            self.system = Opts(**opt_args)
            self.channels = channels
            self.rf_spoil = rf_spoil
            
        self.track_time = 0
        self.rf_spoil_idx = 0
        self.rf_spoil_phase = 0
        
        self.seq = pp.Sequence(system = self.system)
        
    def increment_rf_spoiling(self):
        self.rf_spoil_idx += 1
        self.rf_spoil_phase = (117*np.pi/180) * self.rf_spoil_idx*self.rf_spoil_idx/2
        self.rf_spoil_phase = self.rf_spoil_phase % (2*np.pi)
        
    def init_seq(self):
        self.rf_spoil_idx = 0
        self.rf_spoil_phase = 0
        self.seq = pp.Sequence(system = self.system)
        
    def add_pseq_to_self(self, pseq, *args, **kwargs):
        pseq.add_to_seq(self, *args, **kwargs)
        
    def add_delay(self, delay):
        self.seq.add_block(pp.make_delay(delay))
        
    def get_seq_time(self):
        wave_data, tfp_excitation, tfp_refocusing, t_adc, fp_adc = self.seq.waveforms_and_times(append_RF=True)

        max_t = 0
        for i in range(4):
            if wave_data[i].size > 0:
                max_t = max(max_t, wave_data[i][0].max())
        
        return max_t
    
    def add_dummy_adc(self):
        self.seq.add_block(pp.make_adc(num_samples=100, duration=100*4e-6, system=self.system, delay = 100e-6), pp.make_delay(1e-3))  
    

    
    