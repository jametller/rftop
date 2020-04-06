#!/usr/bin/python3

import sys
import subprocess
import curses
import time

class pow_reader:
    def __init__ (self, input_stream, signal_threshold = 10.0):
        self.__input_stream = input_stream
        self.__signal_threshold = signal_threshold
        self.__dict = {}
    def process_line (self):
        line = str(self.__input_stream.readline (),'utf-8')
        data = line.split (", ")
        timestamp = data[0] + "T" + data[1]
        base_fq = float(data[2])
        step = float (data[4])
        for i in range(7,len(data)):
            current_fq = base_fq + step * (i-6)
            if float(data[i]) >= self.__signal_threshold:
                if current_fq in self.__dict:
                    self.__dict[current_fq][0] = timestamp
                    self.__dict[current_fq][1] = data[i]
                    self.__dict[current_fq][2] += 1
                else:
                    self.__dict[current_fq] = [timestamp,data[i],1]
        return self.__dict

def main (stdscr):
    stdscr.clear()
    
    proc = subprocess.Popen(['rtl_power','-p','1','-i','4','-f','146M:170M:5k'], stdout=subprocess.PIPE)
    pr = pow_reader (proc.stdout)
    stdscr.addstr(0, 0, 'Freq. (Hz)\tLast Seen\tSig. Strength\tIterations')
    stdscr.addstr(1, 0, '--------------------------------------------------------------------------------')
    try:
        while True:
            freq_map = pr.process_line()
            i=2
            for freq in sorted(freq_map.keys()):
                stdscr.addstr(i, 0, '{}\t{}\t{}\t{}'.format(freq, freq_map[freq][0], freq_map[freq][1], freq_map[freq][2]))
                i+=1
            stdscr.refresh()
    except:
        print("Unexpected error:", sys.exc_info()[0])
        proc.kill()
        raise


if __name__ == "__main__":
    # execute only if run as a script
    curses.wrapper(main)
