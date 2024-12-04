import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_Base import Pseq_Base
import numpy as np

class PSeq_Excite_PE(Pseq_Base):
    
    def __init__(self, pseq=None, duration = 6e-3, thickness = 1e-3, 
                 tbw = 4, flip = 50, app = 0.4, 
                 fov = 200e-3, N_pe = 0,
                 max_slew = 100,
                 do_refocus = True,
                 *args, **kwargs):
        
        super().__init__(pseq, *args, **kwargs)
        
        self.duration = duration
        self.do_refocus = do_refocus
        self.fov = fov
        self.N_pe = N_pe
        self.thickness = thickness
        self.tbw = tbw
        self.flip = flip
        self.app = app
        
        if max_slew is not None:
            self.slew = self.system.gamma*max_slew
        else:
            self.slew = self.system.max_slew

        self.rfp, self.gss, self.gss_re = pp.make_sinc_pulse(flip_angle=self.flip, apodization=self.app, duration=self.duration, 
                                                system=self.system, time_bw_product=self.tbw, delay=self.system.rf_dead_time,
                                                slice_thickness=self.thickness, return_gz=True, max_slew = self.slew)
        
        self.refocus_time = 0
        if N_pe > 0:
            self.pe_areas = (np.arange(N_pe) - N_pe//2)/fov
            pe_temp0 = pp.make_trapezoid(channel = self.channels[0], area=self.pe_areas[0], system=self.system)
            pe_temp1 = pp.make_trapezoid(channel = self.channels[0], area=self.pe_areas[-1], system=self.system)
            self.refocus_time = pp.calc_duration(pe_temp0, pe_temp1)
        if do_refocus:
            if pp.calc_duration(self.gss_re) >= self.refocus_time:
                self.refocus_time = pp.calc_duration(self.gss_re)
            else:
                self.gss_re = pp.make_trapezoid(channel = self.channels[2], duration = self.refocus_time, 
                                                area=self.gss_re.area, system=self.system)
            
        
    def make_default_seq(self, ie0 = 0, ie1 = 0):
        self.init_seq()
        
        self.gss.channel = self.channel[2]
        self.gss_re.channel = self.channel[2]
        self.seq.add_block(self.rfp, self.gss)
        
        if self.N_pe>0 and self.do_refocus:
            pe0 = pp.make_trapezoid(channel = self.channels[0], duration=self.refocus_time, area=self.pe_areas[ie0], system=self.system)
            pe1 = pp.make_trapezoid(channel = self.channels[1], duration=self.refocus_time, area=self.pe_areas[ie1], system=self.system)
            self.seq.add_block(pe0, pe1, self.gss_re)
        elif self.N_pe>0 and not self.do_refocus:
            pe0 = pp.make_trapezoid(channel = self.channels[0], duration=self.refocus_time, area=self.pe_areas[ie0], system=self.system)
            pe1 = pp.make_trapezoid(channel = self.channels[1], duration=self.refocus_time, area=self.pe_areas[ie1], system=self.system)
            self.seq.add_block(pe0, pe1)
        elif self.N_pe<=0 and self.do_refocus:
            self.seq.add_block(self.gss_re)

    def add_to_seq(self, pseq0, ie0 = 0, ie1 = 0, offset=0):
        self.rfp.freq_offset = self.gss.amplitude * offset
        
        if pseq0.rf_spoil:
            self.rfp.phase_offset = pseq0.rf_spoil_phase
            
            
        self.gss.channel = pseq0.channels[2]
        self.gss_re.channel = pseq0.channels[2]
        pseq0.seq.add_block(self.rfp, self.gss)
        pseq0.track_time = pseq0.track_time + pp.calc_duration(self.gss)
        
        
        if self.N_pe>0 and self.do_refocus:
            pe0 = pp.make_trapezoid(channel = pseq0.channels[0], duration=self.refocus_time, area=self.pe_areas[ie0], system=self.system)
            pe1 = pp.make_trapezoid(channel = pseq0.channels[1], duration=self.refocus_time, area=self.pe_areas[ie1], system=self.system)
            pseq0.seq.add_block(pe0, pe1, self.gss_re)
            pseq0.track_time = pseq0.track_time + pp.calc_duration(pe0, pe1, self.gss_re)
        elif self.N_pe>0 and not self.do_refocus:
            pe0 = pp.make_trapezoid(channel = pseq0.channels[0], duration=self.refocus_time, area=self.pe_areas[ie0], system=self.system)
            pe1 = pp.make_trapezoid(channel = pseq0.channels[1], duration=self.refocus_time, area=self.pe_areas[ie1], system=self.system)
            pseq0.seq.add_block(pe0, pe1)
            pseq0.track_time = pseq0.track_time + pp.calc_duration(pe0, pe1)
        elif self.N_pe<=0 and self.do_refocus:
            pseq0.seq.add_block(self.gss_re)
            pseq0.track_time = pseq0.track_time + pp.calc_duration(self.gss_re)
            

    def get_duration(self):
        dur = pp.calc_duration(self.rfp, self.gss)
        if self.do_refocus or self.N_pe > 0:
            dur += self.refocus_time
        return dur
    
    def get_duration_from_excite(self):
        dur = 0.5*pp.calc_duration(self.rfp, self.gss)
        if self.do_refocus or self.N_pe > 0:
            dur += self.refocus_time
        return dur