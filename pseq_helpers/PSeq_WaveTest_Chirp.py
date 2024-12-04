import pypulseq as pp
from pypulseq.opts import Opts
from .PSeq_WaveTest import PSeq_WaveTest
import numpy as np
from scipy.signal import windows


def get_chirp(dt, t_chirp, f1, f2, max_krange = 0, max_kmax = 0, gmax=30e-3, smax=100):
    tt = np.arange(0, t_chirp, dt)
    ft = f1 + (f2 - f1)*tt/t_chirp

    Gct = gmax*np.sin(2*np.pi*(f1*tt + (f2 - f1)*tt**2/2/t_chirp))
 
    set = smax / (2 * np.pi * gmax * ft + 1e-16)
    set[set>1] = 1

    blip = set * Gct
    
    m0_min, m0_max = get_m0_range(blip, dt)
    if max_kmax > 0:
        if m0_max <= max_kmax:
            np.hstack([blip, 0])
        else:
            # print('Reducing:', m0_max, max_kmax)
            return get_chirp(dt, t_chirp, f1, f2, max_krange, max_kmax, 0.99*max_kmax/m0_max*gmax, smax)
    if max_krange > 0:
        if (m0_max-m0_min) <= max_krange:
            np.hstack([blip, 0])
        else:
            # print('Reducing:', (m0_max-m0_min), max_krange)
            return get_chirp(dt, t_chirp, f1, f2, max_krange, max_kmax, 0.99*max_krange/(m0_max-m0_min)*gmax, smax)
    
    return np.hstack([blip, 0])

def trap_balance(wave, dt, gmax=30e-3, smax=100, delay = 0.5e-3, gamma = 42576000):
    m0_min, m0_max = get_m0_range(wave, dt)
    m0_balance = (m0_max-m0_min)/2 + m0_min
    # print(f'{m0_balance = }')
    
    g_temp = pp.make_trapezoid(channel='z', area = -m0_balance, max_grad=gamma*gmax, max_slew=gamma*smax)
    
    ramp_N = int(np.ceil(g_temp.rise_time/dt)+1)
    flat_N = int(np.ceil(g_temp.flat_time/dt))
    amp = g_temp.amplitude/gamma
    
    refocus = [np.linspace(0, amp, ramp_N), amp*np.ones(flat_N), np.linspace(amp, 0, ramp_N)]
    refocus = np.hstack(refocus)
    
    return np.hstack([refocus, np.zeros(int(delay/dt)), wave])


def kais_balance(wave, dt, duration = 2e-3, gmax=30e-3, smax=100, delay = 0.5e-3, gamma = 42576000):
    m0_min, m0_max = get_m0_range(wave, dt)
    m0_balance = (m0_max-m0_min)/2 + m0_min
    # print(f'{m0_balance = }')
    
    ww = windows.kaiser(int(duration/dt), 14)
    ww[0] = 0
    ww[-1] = 0
    
    scale = -m0_balance / (gamma * dt * np.sum(ww))
    ww *= scale
    
    return np.hstack([ww, np.zeros(int(delay/dt)), wave])

def get_m0_range(wave, dt, gamma = 42576000):
    m0 = gamma*dt*np.cumsum(wave)
    return m0.min(), m0.max()


def prep_all_chirps(thickness = 1e-3, dt = 10e-6, gmax = 30e-3, smax = 150, all_f2 = [5e3, 15e3], all_t_chirp = [20e-3, 40e-3]):
    
    gamma = 42576000
    f1 = 0

    all_chirps = []
    for f2 in all_f2:
        for t_chirp in all_t_chirp:
            
            chirp = get_chirp(dt, t_chirp, f1, f2, gmax=gmax, smax=smax, max_kmax = 0.3/thickness)
            
            chirp_r = get_chirp(dt, t_chirp, f1, f2, gmax=gmax, smax=smax, max_krange = 0.6/thickness)
            chirp2 = trap_balance(chirp_r, dt, delay=0.5e-3, gmax=0.9*gmax, smax=0.9*smax)
            chirp3 = trap_balance(chirp_r, dt, delay=2e-3, gmax=0.9*gmax, smax=0.9*smax)
            
            areas = [gamma*dt*chirp.sum(), gamma*dt*chirp2.sum(), gamma*dt*chirp3.sum()]
            
            all_chirps.append({
                'f2': f2,
                't_chirp': t_chirp,
                'mode': 0,
                'chirp': chirp,
                'area': areas[0],        
                })
            
            all_chirps.append({
                'f2': f2,
                't_chirp': t_chirp,
                'mode': 1,
                'chirp': chirp2,
                'area': areas[1],     
            })
            
            all_chirps.append({
                'f2': f2,
                't_chirp': t_chirp,
                'mode': 2,
                'chirp': chirp3,
                'area': areas[2],     
            })
            
    return all_chirps



class PSeq_WaveTest_Chirp(PSeq_WaveTest):
    
    def __init__(self, pseq=None, 
                 *args, **kwargs):
        
        super().__init__(pseq, *args, **kwargs)
        
        
    def prep_waves(self):
        self.all_chirps = prep_all_chirps(thickness = 1e-3, 
                                    dt = self.system.grad_raster_time, 
                                    gmax = 0.98*self.system.max_grad/self.system.gamma, 
                                    smax = 0.98*self.slew/self.system.gamma)
        
        self.N_waves = len(self.all_chirps)

        self.all_test_waves = []
        self.all_test_waves_neg = []
        self.all_refocus_areas = []
        for i in range(self.N_waves):
            wave = pp.make_arbitrary_grad(channel = self.channels[2], waveform=self.system.gamma*self.all_chirps[i]['chirp'],
                                delay=self.wave_delay, system=self.system)
            self.all_test_waves.append(wave)
            self.all_refocus_areas.append(-self.all_chirps[i]['area'])
            
            wave = pp.make_arbitrary_grad(channel = self.channels[2], waveform=-self.system.gamma*self.all_chirps[i]['chirp'],
                                delay=self.wave_delay, system=self.system)
            self.all_test_waves_neg.append(wave)

            