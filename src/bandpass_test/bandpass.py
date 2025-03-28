import scipy.signal as signal
import numpy as np
import math
import matplotlib.pyplot as plt

#create a butterworth bandpass filter with cutoff frequency [lowcut, highcut]
def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    sos = signal.butter(order, [low,high], analog=False, btype='band', output='sos')
    return sos

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    filt_ord = math.ceil(order / 2.0)
    try:
        sos = butter_bandpass(lowcut,highcut, fs, filt_ord)
        padl = 3 * (2 * len(sos) + 1 - min((sos[:, 2] == 0).sum(),
                            (sos[:, 5] == 0).sum()))
        if data.shape[0] < padl:
            padl = data.shape[0] - 1 
        y = signal.sosfiltfilt(sos, data, padlen = padl )
    except ValueError as e:
        raise
    return y


#smooth data by applying median filter and lowpass
def smooth_data(data, highcut, fs, win_size = 0.5):
    nq = fs * 0.5
    
    N = int(data.shape[0] * 0.1)
    
    """prefix_pad = data[:N]
    suffix_pad = data[data.shape[0]-N:]
    
    prefix_pad = prefix_pad * 2 - np.flip(prefix_pad)
    suffix_pad = suffix_pad * 2 - np.flip(suffix_pad)
    
    
    input_data = np.append(prefix_pad,data)
    input_data = np.append(input_data,suffix_pad)"""
    
    try:
        smoothed_data = signal.medfilt(data,int(win_size * fs) + int(win_size * fs) % 2 + 1)
        lpf = signal.firwin(int(win_size * fs) + int(win_size * fs) % 2 + 1,(highcut / nq), window='hamming')
        smoothed_data =  signal.convolve(smoothed_data, lpf, mode='same')
    except ValueError as e:
        raise
    return smoothed_data

if __name__ == "__main__":

    lowcut = 1.9
    highcut = 2.1
    fs = 5.0 # sampling frequency
    order = 5
    win_size = 0.5

    # Example data
    # Parameters for the sinusoidal signal
    n = 200  # Number of data points
    fs = 5.0  # Sampling frequency in Hz
    t = np.linspace(0, n / fs, n)  # Time vector
    amplitude_0_5hz = 0.2  # Amplitude of the 0.5 Hz sinusoidal signal
    amplitude_2hz = 0.1  # Amplitude of the 2 Hz sinusoidal signal
    mean = 1.0  # Mean of the sinusoidal signal
    frequency_0_5hz = 0.5  # Frequency of the first sinusoidal signal in Hz
    frequency_2hz = 2.0  # Frequency of the second sinusoidal signal in Hz

    # Generate the 0.5 Hz sinusoidal signal
    sinus_signal_0_5hz = mean + amplitude_0_5hz * np.sin(2 * np.pi * frequency_0_5hz * t)

    # Generate the 2 Hz sinusoidal signal
    sinus_signal_2hz = amplitude_2hz * np.sin(2 * np.pi * frequency_2hz * t)

    # Combine the two sinusoidal signals
    combined_sinus_signal = sinus_signal_0_5hz + sinus_signal_2hz

    # Add random noise
    noise = np.random.normal(0, 0.05, n)  # Gaussian noise with mean 0 and standard deviation 0.05
    input_data = combined_sinus_signal # + noise

    # ld_smoothed = smooth_data(input_data, highcut, fs, win_size = 0.5)
    ld_smoothed = input_data
    ld_bandpassed = butter_bandpass_filter(ld_smoothed, lowcut / 2.0, highcut, fs, order)

    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(sinus_signal_0_5hz, label="0.5 Hz", alpha=0.7)
    plt.plot(sinus_signal_2hz, label="2 Hz", alpha=0.7)
    plt.plot(input_data, label="Input Data", alpha=0.7)
    # plt.plot(ld_smoothed, label="Smoothed Data", alpha=0.7)
    plt.plot(ld_bandpassed, label="Bandpassed Data", alpha=0.7)
    plt.xlabel("Sample Index")
    plt.ylabel("Amplitude")
    plt.title("Data Processing: Original, Smoothed, and Bandpassed")
    plt.legend()
    plt.grid()
    plt.show()