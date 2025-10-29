
# from __future__ import division # uncomment this if using Python 2.7
import numpy as np


def rect_old(t, T0, T):
    """ rect((t-T0)/T) """
    out = np.zeros(len(t))
    _fs = 1 / (t[1] - t[0])  # estimated sampling freq
    idx_T0 = int(T0 *_fs) + 1
    deltaT = int(T *_fs)
    out[max(0, idx_T0 - int(deltaT/2)):min(len(t), idx_T0 + int(deltaT/2))] = 1
    return out


def triang(t, T0, T):
    """triang((t-T0)/T)"""
    return (1 - np.abs((t - T0) / T)) *rect(t, T0, 2*T)


def u(t, T0):
    """ u(t-T0) """
    return 0.5 * (np.sign(t - T0) + 1)


def rect(t, T0, T):
    """ rect((t-T0)/T) """
    return u(t, T0 - T/2) - u(t, T0 + T/2)


def RC_h(t,tau,T0=0):
    """ 1/tau * exp(-t/tau) u(t) """
    return (1 / tau) * np.exp(-t / tau) * u(t, T0)# uncomment the line above when you're ready

class LTI:
    """ Linear time-invariant system object """
    def __init__(self, name, imp_resp):
        self.name = name
        self.h = imp_resp
        self.H = self._setFrequencyResponse()

    def transform(self, x):
        return signal.fftconvolve(x, self.h, mode='same') / np.sum(np.abs(x))

    def _setFrequencyResponse(self):
        return np.fft.fft(self.h)/np.sum(np.abs(self.h))
# uncomment the line above when you're ready

# Impulse responses    
def hlp(t,B):
    return 2*B*np.sinc(2*B*t)

def hbp(t,Bstart,Bstop):
    B = Bstop - Bstart
    f0 = Bstart + B/2
    return hlp(t,B/2)*np.cos(2*np.pi*f0*t)# uncomment the line above when you're ready

def u(t,T0):
    """ u(t-T0) """
    return 0.5*(np.sign(t-T0)+1)

def rect(t,T0,T):
    """ rect((t-T0)/T) """
    return u(t,T0-T/2) - u(t,T0+T/2)# uncomment the line above when you're ready

def RC_h(t,tau,T0=0):
    """ 1/tau * exp(-t/tau) u(t) """
    return (1 / tau) * np.exp(-t / tau) * u(t, T0)# uncomment the line above when you're ready

class LTI:
    """ Linear time-invariant system object """    
    def __init__(self, name, imp_resp):
        self.name = name
        self.h = imp_resp
        self.H = self._setFrequencyResponse()
        
    def transform(self, x):
        return signal.fftconvolve(x, self.h, mode='same') / np.sum(np.abs(x))
    
    def _setFrequencyResponse(self):
        return np.fft.fft(self.h)/np.sum(np.abs(self.h))# uncomment the line above when you're ready

def u(t,T0):
    """ u(t-T0) """
    return 0.5*(np.sign(t-T0)+1)

def rect(t,T0,T):
    """ rect((t-T0)/T) """
    return u(t,T0-T/2) - u(t,T0+T/2)# uncomment the line above when you're ready

def RC_h(t,tau,T0=0):
    """ 1/tau * exp(-t/tau) u(t) """
    return (1 / tau) * np.exp(-t / tau) * u(t, T0)# uncomment the line above when you're ready

class LTI:
    """ Linear time-invariant system object """    
    def __init__(self, name, imp_resp):
        self.name = name
        self.h = imp_resp
        self.H = self._setFrequencyResponse()
        
    def transform(self, x):
        return signal.fftconvolve(x, self.h, mode='same') / np.sum(np.abs(x))
    
    def _setFrequencyResponse(self):
        return np.fft.fft(self.h)/np.sum(np.abs(self.h))# uncomment the line above when you're ready

def u(t,T0):
    """ u(t-T0) """
    return 0.5*(np.sign(t-T0)+1)

def rect(t,T0,T):
    """ rect((t-T0)/T) """
    return u(t,T0-T/2) - u(t,T0+T/2)# uncomment the line above when you're ready

def RC_h(t,tau,T0=0):
    """ 1/tau * exp(-t/tau) u(t) """
    return (1 / tau) * np.exp(-t / tau) * u(t, T0)# uncomment the line above when you're ready

class LTI:
    """ Linear time-invariant system object """    
    def __init__(self, name, imp_resp):
        self.name = name
        self.h = imp_resp
        self.H = self._setFrequencyResponse()
        
    def transform(self, x):
        return signal.fftconvolve(x, self.h, mode='same') / np.sum(np.abs(x))
    
    def _setFrequencyResponse(self):
        return np.fft.fft(self.h)/np.sum(np.abs(self.h))# uncomment the line above when you're ready

# Impulse responses    
def hlp(t,B):
    return 2*B*np.sinc(2*B*t)

def hbp(t,Bstart,Bstop):
    B = Bstop - Bstart
    f0 = Bstart + B/2
    return hlp(t,B/2)*np.cos(2*np.pi*f0*t)