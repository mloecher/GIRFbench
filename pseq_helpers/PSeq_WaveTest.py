import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_Base import Pseq_Base
import numpy as np

class PSeq_WaveTest(Pseq_Base):
    
    def __init__(self, pseq=None, 
                 dt_adc = 8e-6,
                 N_adc = 8000,
                 do_adc = True,
                 meas_delay = 80e-3,  # only played when ADC is off for skope
                 N_waves = 12,
                 adc_delay = 1e-3,
                 wave_delay = 2e-3,
                 slew = None,
                 *args, **kwargs):
        
        super().__init__(pseq, *args, **kwargs)
        
        self.N_waves = N_waves
        self.adc_delay = adc_delay
        self.wave_delay = wave_delay

        self.dt_adc = dt_adc
        self.N_adc = N_adc
        
        self.do_adc = do_adc
        self.meas_delay = meas_delay

        if slew is not None:
            self.slew = self.system.gamma*slew
        else:
            self.slew = self.system.max_slew
        
        if self.do_adc:
            if self.N_adc > self.system.adc_samples_limit:
                self.adc_segments, self.adc_samples_seg = pp.calc_adc_segments(self.N_adc, self.dt_adc, self.system)
                self.N_adc = self.adc_segments * self.adc_samples_seg
            else:
                self.adc_segments, self.adc_samples_seg = (0, 0)
                
            self.adc = pp.make_adc(num_samples=self.N_adc, dwell=self.dt_adc, 
                                delay=self.adc_delay, system=self.system)
        else:
            self.pp_delay = pp.make_delay(self.meas_delay)

        self.prep_waves()
        
    def prep_waves(self):
        print('WARNING: PSeq_WaveTest prep_waves shouldnt be called')
             
    def make_default_seq(self, idx = 0, polarity = 1):
        self.init_seq()
        
        blocks_to_play = []
        
        if polarity == 1:
            self.all_test_waves[idx].channel = self.channels[2]
            blocks_to_play.append(self.all_test_waves[idx])
        elif polarity == -1:
            self.all_test_waves_neg[idx].channel = self.channels[2]
            blocks_to_play.append(self.all_test_waves_neg[idx])
        
        if self.do_adc:
            blocks_to_play.append(self.adc)
        else:
            blocks_to_play.append(self.pp_delay)
            
        self.seq.add_block(*blocks_to_play)
        
        
    def add_to_seq(self, pseq0, idx=0, polarity = 1):
        
        blocks_to_play = []
        
        if polarity == 1:
            self.all_test_waves[idx].channel = pseq0.channels[2]
            blocks_to_play.append(self.all_test_waves[idx])
        elif polarity == -1:
            self.all_test_waves_neg[idx].channel = pseq0.channels[2]
            blocks_to_play.append(self.all_test_waves_neg[idx])
        
        if self.do_adc:
            if pseq0.rf_spoil:
                self.adc.phase_offset = pseq0.rf_spoil_phase    
            blocks_to_play.append(self.adc)
            if len(blocks_to_play) == 1:
                blocks_to_play.append(pp.make_delay(pp.calc_duration(self.adc)))
        else:
            blocks_to_play.append(self.pp_delay)
            
        pseq0.seq.add_block(*blocks_to_play)
        pseq0.track_time = pseq0.track_time + pp.calc_duration(*blocks_to_play)

    def get_duration(self, idx = 0, polarity = 1):
        
        blocks_to_play = []
        
        if polarity == 1:
            self.all_test_waves[idx].channel = self.channels[2]
            blocks_to_play.append(self.all_test_waves[idx])
        elif polarity == -1:
            self.all_test_waves_neg[idx].channel = self.channels[2]
            blocks_to_play.append(self.all_test_waves_neg[idx])
        
        if self.do_adc: 
            blocks_to_play.append(self.adc)
            if len(blocks_to_play) == 1:
                blocks_to_play.append(pp.make_delay(pp.calc_duration(self.adc)))
        else:
            blocks_to_play.append(self.pp_delay)
            
        dur = pp.calc_duration(*blocks_to_play)
        
        return dur
            
