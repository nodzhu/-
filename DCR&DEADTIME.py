import visa
import time
import re
import numpy as np
import math
import matplotlib.pyplot as plt

rm = visa.ResourceManager()
print(rm.list_resources())
# Get information about all the devices connected to your computer
E3647A = rm.open_resource('ASRL21::INSTR')
E3647A2 = rm.open_resource('ASRL1::INSTR')
scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')


# Used to connect power and oscilloscope

def VquenchDCR(time):
    E3647A = rm.open_resource('ASRL21::INSTR')
    E3647A2 = rm.open_resource('ASRL1::INSTR')
    scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')
    x = np.arange(1, 3.05, 0.1)
    # Set the x-axis measurement range/ vquench range
    y = []
    y_counts = []
    # used to store dcr and counts number
    scope.timeout = 50000
    E3647A.timeout = 5000
    E3647A2.timeout = 5000
    # set timeout for scope and powermeter
    scope.clear()
    # Clear the settings in the scope
    scope.write('*RST')
    # reset the scope parameter
    E3647A2.write('*RST')
    # reset the powermeter
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':VOLT %G' % (3.3 + 0.01))
    # time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':CURR %G' % (0.01))
    # time.sleep(0.5)
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':VOLT %G' % (1 - 0.03))
    # set vequench
    # time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':CURR %G' % (0.01))
    # time.sleep(0.5)
    E3647A2.write(':OUTP %d' % (1))
    E3647A2.write('*CLS')
    # set power 1
    E3647A.write('*CLS')
    E3647A.write('*RST')
    E3647A.write('*CLS')
    E3647A.write(':VOLT %G' % 16)
    E3647A.write(':CURR %G' % (0.01))
    E3647A.write(':OUTP %d' % (1))
    # set voltage at breakdown voltage, current at 0.01a and turn output on
    for i in range(0, len(x)):
        scope.write("VBS 'app.Acquisition.C1.Verscale = 1.0'")
        scope.write("VBS 'app.Acquisition.C1.VerOffset = 0.0'")
        # set voltage/div and voltage offset
        scope.write("""VBS 'app.Acquisition.Horizontal.HorScale = %f '""" %time)
        scope.write("VBS 'app.Acquisition.Horizontal.MaxSamples=12500000'")
        scope.write("VBS 'app.Acquisition.C1.Position = 0.0'")
        # set horizontal/div (timebase/div) and horizontal offset
        scope.write("""VBS 'app.Acquisition.TriggerMode = "stopped" ' """)
        scope.write("VBS 'app.Acquisition.Trigger.TrigLevel = 1.8'")
        # scope.write("""VBS 'app.Acquisition.TriggerMode = "Auto" ' """)
        scope.write("""VBS 'app.Acquisition.TriggerMode = "Single" ' """)
        # set triggermode and trigger level
        scope.write("VBS 'app.measure.clearall' ")
        scope.write("VBS 'app.measure.showmeasure = True' ")
        scope.write("VBS 'app.measure.statson = True' ")
        scope.write("VBS 'app.measure.p1.view = True' ")
        scope.write("VBS 'app.measure.p2.view = True' ")
        # clearall and open the panel
        # scope.write("""VBS 'app.measure.p1.paramengine = "freq" ' """)
        scope.write("""VBS 'app.measure.p2.paramengine = "EdgeAtLevel" ' """)
        scope.write("""VBS 'app.measure.p2.Operator.PercentLevel = 50 ' """)
        # set the threshold level percentage
        # set the measurement
        scope.write("""VBS 'app.measure.p2.sourcel = "C1" ' """)
        # measure source
        a = []
        a2 = []
        # a2 is used to store counts number
        for i in range(0, 1):

            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            #trigger twice
            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            # read counts(or photons)
            counts = counts[4:]
            counts = float(counts)
            print(counts)
            counts = round(counts)
            print('\n')
            print(counts)
            f1 = 1 / (time * 10 / counts)
            a.append(f1)
            a2.append(counts)
        b = 0
        for i in range(len(a)):
            b += a[i]
        c = b / len(a)

        b1 = 0
        for i in range(len(a2)):
            b1 += a2[i]
        f2 = []
        f2.append(c)
        print(f2)
        a3 = 0
        while b1 < 1:
            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))

            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            counts = counts[4:]
            counts = float(counts)
            counts = round(counts)
            f1 = 1 / (time * 10 / counts)
            f2.append(f1)
            b1 = b1 + counts
        for i in range(len(f2)):
            a3 += f2[i]
        c2 = a3 / len(f2)
        # get mean frequence
        E3647A2.write('*CLS')
        E3647A2.write(':VOLT:STEP %G' % (0.1))
        E3647A2.write(':VOLT %s' % ('UP'))
        y.append(c2)
        print(y)
        y_counts.append(b1)
        print(y_counts)
        scope.clear()
    E3647A2.close()
    E3647A.close()
    scope.close()
    return y, y_counts

def BreakdownVoltage(vq):
    #used to measure breakdown voltage
    E3647A = rm.open_resource('ASRL21::INSTR')
    E3647A2 = rm.open_resource('ASRL1::INSTR')
    scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')
    scope.timeout = 5000
    E3647A.timeout = 5000
    E3647A2.timeout = 5000
    # Connect the device and set the wait time for the device to transfer information
    scope.clear()
    # connect instrument and clean the scope
    scope.write('*RST')
    # reset the scope parameter
    E3647A2.write('*RST')
    # reset the powermeter
    E3647A2.write('*CLS')
    # Clean up the buffer to prevent buffer overflow
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':VOLT %G' % (3.31))
    # set output1 voltage at 3.3v
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':CURR %G' % (0.01))
    # set output1 current at 0.01A
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':VOLT %G' % (vq - 0.02))
    # set output2 voltage as v quench
    #0.02 is the deviation of the power supply
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':CURR %G' % (0.01))
    # set output2 current at 0.01A
    E3647A2.write(':OUTP %d' % (1))
    # turn on the power (turn on the output1 & output2)
    E3647A2.write('*CLS')
    # set power 2
    E3647A.write('*RST')
    E3647A.write('*CLS')
    E3647A.write(':INST %s' % ('OUTP1'))
    E3647A.write(':VOLT %G' % (14.3))
    # Set the initial vhv as 14.3v and keep increasing vhv to find the breakdown voltage
    bv = 14.3
    time.sleep(0.5)
    E3647A.write(':INST %s' % ('OUTP1'))
    E3647A.write(':CURR %G' % (0.01))
    E3647A.write('*CLS')
    E3647A.write(':OUTP %d' % (1))
    E3647A.write('*CLS')
    # set power 1
    var = 0
    # When vhv reaches the breakdown voltage, a pulse will be generated, and var is the voltage of the generated pulse.
    while var < 2:
        E3647A.write('*CLS')
        E3647A.write(':VOLT:STEP %G' % (0.1))
        #Set the voltage interval to 0.1v
        E3647A.write(':VOLT %s' % ('UP'))
        # increase the voltage
        bv = bv + 0.1
        #print(bv)
        scope.write("VBS 'app.Acquisition.C1.Verscale = 1.0'")
        scope.write("VBS 'app.Acquisition.C1.VerOffset = 0.0'")
        scope.write("VBS 'app.Acquisition.Horizontal.HorScale = 0.00000005'")
        scope.write("VBS 'app.Acquisition.C1.Position = 0.0'")
        scope.write("""VBS 'app.Acquisition.TriggerMode = "stopped" ' """)
        scope.write("VBS 'app.Acquisition.Trigger.TrigLevel = 1.8'")
        scope.write("""VBS 'app.Acquisition.TriggerMode = "Auto" ' """)
        time.sleep(0.5)
        #Waiting for the oscilloscope for 0.5 seconds to get the new data
        # scope.write("""VBS 'app.Acquisition.TriggerMode = "Single" ' """)
        scope.write("VBS 'app.measure.clearall' ")
        scope.write("VBS 'app.measure.showmeasure = True' ")
        scope.write("VBS 'app.measure.statson = True' ")
        scope.write("VBS 'app.measure.p1.view = True' ")
        scope.write("""VBS 'app.measure.p1.paramengine = "top" ' """)
        scope.write("""VBS 'app.measure.p1.sourcel = "C1" ' """)
        var = scope.query(r"""vbs? 'return=app.measure.p1.out.result.value' """)
        print(var)
        # get top voltage value
        var = var[4:]
        var = float(var)
        print(var)
    print(bv)
    bv = round(bv, 1)
    print(bv)
    bv = bv - 0.1
    #Since the breakdown voltage is the voltage at which the pulse has not occurred, subtract 0.1 from here.
    print('the breakdown voltage is', bv )
    E3647A2.close()
    E3647A.close()
    scope.close()
    return bv


def DCR(bv, vq, time, minimumcounts):
#bv is breakdown voltage, vq is quench volage, time is the length of time for each unit on the oscilloscope
#minimumcounts is the minimum number of pulses per point
#get the mean frequence from the oscilloscpe
    E3647A = rm.open_resource('ASRL21::INSTR')
    E3647A2 = rm.open_resource('ASRL1::INSTR')
    scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')
    x = np.arange(0.1, 2.55, 0.1)
    # Set the x-axis measurement range/ vhv range
    y = []
    y_counts = []
    #used to store dcr and counts number
    scope.timeout = 50000
    E3647A.timeout = 5000
    E3647A2.timeout = 5000
    #set timeout for scope and powermeter
    scope.clear()
    #Clear the settings in the scope
    scope.write('*RST')
    # reset the scope parameter
    E3647A2.write('*RST')
    #reset the powermeter
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':VOLT %G' % (3.3 + 0.01))
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':CURR %G' % (0.01))
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':VOLT %G' % (vq - 0.03))
    # set vequench
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':CURR %G' % (0.01))
    E3647A2.write(':OUTP %d' % (1))
    E3647A2.write('*CLS')
    # set power 1
    E3647A.write('*CLS')
    E3647A.write('*RST')
    E3647A.write('*CLS')
    E3647A.write(':VOLT %G' % (bv + 0.1))
    E3647A.write(':CURR %G' % (0.01))
    E3647A.write(':OUTP %d' % (1))
    # set voltage at breakdown voltage, current at 0.01a and turn output on
    for i in range(0, len(x)):
        scope.write("VBS 'app.Acquisition.C1.Verscale = 1.0'")
        scope.write("VBS 'app.Acquisition.C1.VerOffset = 0.0'")
        # set voltage/div and voltage offset
        scope.write("VBS 'app.Acquisition.Horizontal.HorScale = %f'" %time)
        scope.write("VBS 'app.Acquisition.Horizontal.MaxSamples=12500000'")
        scope.write("VBS 'app.Acquisition.C1.Position = 0.0'")
        # set horizontal/div (timebase/div) and horizontal offset
        scope.write("""VBS 'app.Acquisition.TriggerMode = "stopped" ' """)
        scope.write("VBS 'app.Acquisition.Trigger.TrigLevel = 1.8'")
        # scope.write("""VBS 'app.Acquisition.TriggerMode = "Auto" ' """)
        scope.write("""VBS 'app.Acquisition.TriggerMode = "Single" ' """)
        # set triggermode and trigger level
        scope.write("VBS 'app.measure.clearall' ")
        scope.write("VBS 'app.measure.showmeasure = True' ")
        scope.write("VBS 'app.measure.statson = True' ")
        scope.write("VBS 'app.measure.p1.view = True' ")
        scope.write("VBS 'app.measure.p2.view = True' ")
        # clearall and open the panel
        scope.write("""VBS 'app.measure.p1.paramengine = "freq" ' """)
        #scope.write("""VBS 'app.measure.p1.Accept.GateByWform = true ' """)
        #scope.write("""VBS 'app.measure.p1.Accept.PercentLevel = 65 ' """)
        scope.write("""VBS 'app.measure.p2.paramengine = "EdgeAtLevel" ' """)
        scope.write("""VBS 'app.measure.p2.Operator.PercentLevel = 50 ' """)
        # set the threshold level percentage
        # set the measurement
        scope.write("""VBS 'app.measure.p1.sourcel = "C1" ' """)
        scope.write("""VBS 'app.measure.p2.sourcel = "C1" ' """)
        # measure source
        a = []
        # a is used to store the mean frequency
        a2 = []
        # a2 is used to store counts number
        for i in range(0, 1):

            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            #trigger twice
            temp_values = scope.query(r"""VBS? 'return=app.measure.p1.mean.result.value'""")
            # read frequency
            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            # read counts(or photons)
            temp_values = temp_values[4:]
            counts = counts[4:]
            temp_values = float(temp_values)
            counts = float(counts)
            counts = round(counts)
            a.append(temp_values)
            a2.append(counts)
        b = 0
        for i in range(len(a)):
            b += a[i]
        c = b / len(a)
        f2 = []
        f2.append(c)
        b1 = 0
        for i in range(len(a2)):
            b1 += a2[i]
        while b1 < minimumcounts:
            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            temp_values = scope.query(r"""VBS? 'return=app.measure.p1.mean.result.value'""")
            # read frequency
            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            # read counts(or photons)
            temp_values = temp_values[4:]
            counts = counts[4:]
            temp_values = float(temp_values)
            counts = float(counts)
            counts = round(counts)
            b1 = b1 + counts
            f2.append(temp_values)
        a3 = 0
        for i in range(len(f2)):
            a3 += f2[i]
        c2 = a3/len(f2)
        # get mean frequence (use the statistics function)
        E3647A.write('*CLS')
        E3647A.write(':VOLT:STEP %G' % (0.1))
        E3647A.write(':VOLT %s' % ('UP'))
        y.append(c2)
        print(y)
        y_counts.append(b1)
        print(y_counts)
        scope.clear()
    E3647A2.close()
    E3647A.close()
    scope.close()
    return y, y_counts


def DCR2(bv, vq, time, minimumcounts):
    E3647A = rm.open_resource('ASRL21::INSTR')
    E3647A2 = rm.open_resource('ASRL1::INSTR')
    scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')
    x = np.arange(0.1, 2.55, 0.1)
    # Set the x-axis measurement range/ vhv range
    y = []
    y_counts = []
    scope.timeout = 8000
    E3647A.timeout = 5000
    E3647A2.timeout = 5000
    scope.clear()
    scope.write('*RST')
    # reset the scope parameter
    E3647A2.write('*RST')
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':VOLT %G' % (3.3 + 0.01))
    #time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':CURR %G' % (0.01))
    #time.sleep(0.5)
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':VOLT %G' % (vq - 0.03))
    # set vequench
    #time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':CURR %G' % (0.01))
    #time.sleep(0.5)
    E3647A2.write(':OUTP %d' % (1))
    E3647A2.write('*CLS')
    # set power 2
    E3647A.write('*CLS')
    E3647A.write('*RST')
    E3647A.write('*CLS')
    E3647A.write(':VOLT %G' % (bv+0.1))
    E3647A.write(':CURR %G' % (0.01))
    E3647A.write(':OUTP %d' % (1))
    # set voltage at 15v current 0.01a and turn output on
    for i in range(0, len(x)):
        scope.write("VBS 'app.Acquisition.C1.Verscale = 1.0'")
        scope.write("VBS 'app.Acquisition.C1.VerOffset = 0.0'")
        # set voltage/div and voltage offset
        scope.write("""VBS 'app.Acquisition.Horizontal.HorScale = 0.1 '""")
        scope.write("VBS 'app.Acquisition.Horizontal.MaxSamples=12500000'")
        scope.write("VBS 'app.Acquisition.C1.Position = 0.0'")
        # set horizontal/div (timebase/div) and horizontal offset
        scope.write("""VBS 'app.Acquisition.TriggerMode = "stopped" ' """)
        scope.write("VBS 'app.Acquisition.Trigger.TrigLevel = 1.8'")
        # scope.write("""VBS 'app.Acquisition.TriggerMode = "Auto" ' """)
        scope.write("""VBS 'app.Acquisition.TriggerMode = "Single" ' """)
        # set triggermode and trigger level
        scope.write("VBS 'app.measure.clearall' ")
        scope.write("VBS 'app.measure.showmeasure = True' ")
        scope.write("VBS 'app.measure.statson = True' ")
        scope.write("VBS 'app.measure.p1.view = True' ")
        scope.write("VBS 'app.measure.p2.view = True' ")
        # clearall and open the panel
        scope.write("""VBS 'app.measure.p2.paramengine = "EdgeAtLevel" ' """)
        scope.write("""VBS 'app.measure.p2.Operator.PercentLevel = 60 ' """)
        # set the threshold level percentage
        # set the measurement
        scope.write("""VBS 'app.measure.p2.sourcel = "C1" ' """)
        # measure source
        a = []
        a2 = []
        # a2 is used to store counts number
        for i in range(0, 1):

            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            # trigger twice
            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            # read counts(or photons)
            counts = counts[4:]
            counts = float(counts)
            print(counts)
            counts = round(counts)
            print('\n')
            print(counts)
            f1 = 1 / ( time * 10/ counts)
            a.append(f1)
            a2.append(counts)
        b = 0
        for i in range(len(a)):
            b += a[i]
        c = b / len(a)

        b1 = 0
        for i in range(len(a2)):
            b1 += a2[i]
        f2 = []
        f2.append(c)
        print(f2)
        a3 = 0
        while b1 < minimumcounts:
            for i in range(0, 2):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(9)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            #trigger twice
            counts = scope.query(r"""VBS? 'return=app.measure.p2.mean.result.value'""")
            # read counts(or photons)
            counts = counts[4:]
            counts = float(counts)
            # print(counts)
            counts = round(counts)
            f1 = 1 / (time * 10/counts)
            #Calculate dcr
            f2.append(f1)
            b1 = b1 + counts
        for i in range(len(f2)):
            a3 += f2[i]
        c2 = a3/len(f2)
        #Calculate the average frequency
        E3647A.write('*CLS')
        E3647A.write(':VOLT:STEP %G' % (0.1))
        E3647A.write(':VOLT %s' % ('UP'))
        y.append(c2)
        print(y)
        y_counts.append(b1)
        print(y_counts)
        scope.clear()
    E3647A2.close()
    E3647A.close()
    scope.close()
    return y, y_counts


def Deadtime(vq1, vq2, vhv):
    E3647A = rm.open_resource('ASRL21::INSTR')
    E3647A2 = rm.open_resource('ASRL1::INSTR')
    scope = rm.open_resource('TCPIP0::169.254.9.2::inst0::INSTR')
    scope.timeout = 5000
    E3647A.timeout = 5000
    E3647A2.timeout = 5000
    scope.clear()
    scope.write('*RST')
    # reset the scope parameter
    E3647A2.write('*RST')
    time.sleep(0.1)
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':VOLT %G' % (3.31))
    #time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP1'))
    E3647A2.write(':CURR %G' % (0.01))
    #time.sleep(0.5)
    E3647A2.write('*CLS')
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':VOLT %G' % (vq1 - 0.02))
    # set vequench
    #time.sleep(0.5)
    E3647A2.write(':INST %s' % ('OUTP2'))
    E3647A2.write(':CURR %G' % (0.01))
    #time.sleep(0.5)
    E3647A2.write(':OUTP %d' % (1))
    E3647A2.write('*CLS')
    # set power 2
    E3647A.write('*CLS')
    E3647A.write('*RST')
    E3647A.write('*CLS')
    E3647A.write(':VOLT %G' % (vhv))
    E3647A.write(':CURR %G' % (0.01))
    E3647A.write(':OUTP %d' % (1))
    x = np.arange(vq1, vq2 + 0.01, 0.05)
    y = []
    for i in range(0, len(x)):
        scope.write("VBS 'app.Acquisition.C1.Verscale = 1.0'")
        scope.write("VBS 'app.Acquisition.C1.VerOffset = 0.0'")
        scope.write("VBS 'app.Acquisition.Horizontal.HorScale = 0.00000005'")
        scope.write("VBS 'app.Acquisition.C1.Position = 0.0'")
        scope.write("""VBS 'app.Acquisition.TriggerMode = "stopped" ' """)
        scope.write("VBS 'app.Acquisition.Trigger.TrigLevel = 1'")
        # scope.write("""VBS 'app.Acquisition.TriggerMode = "Auto" ' """)
        scope.write("""VBS 'app.Acquisition.TriggerMode = "Single" ' """)
        scope.write("VBS 'app.measure.clearall' ")
        scope.write("VBS 'app.measure.showmeasure = True' ")
        scope.write("VBS 'app.measure.statson = True' ")
        scope.write("VBS 'app.measure.p1.view = True' ")
        scope.write("""VBS 'app.measure.p1.paramengine = "width" ' """)
        scope.write("""VBS 'app.measure.p1.sourcel = "C1" ' """)
        a = []
        for i in range(0, 10):
            for i in range(0, 3):
                r = scope.query(r"""vbs? 'return=app.acquisition.acquire( 0.1 , True )' """)
                r = scope.query(r"""vbs? 'return=app.WaitUntilIdle(5)' """)
                if r == 0:
                    print("Time out from WaitUntilIdle, return = %s" % (r))
            # trigger 3 times
            var = scope.query(r"""vbs? 'return=app.measure.p1.mean.result.value' """)
            # get mean time (use the statistics function)
            var = var[4:]
            var = float(var)
            a.append(var)
            print(a)
        b = 0
        for i in range(len(a)):
            b += a[i]
        c = b / len(a)
        E3647A2.write('*CLS')
        E3647A2.write(':VOLT:STEP %G' % (0.05))
        #time.sleep(1)
        E3647A2.write(':VOLT %s' % ('UP'))
        time.sleep(2)
        y.append(c)
        scope.clear()
    E3647A2.close()
    E3647A.close()
    scope.close()
    return y


def Polyfitting(x, y):
    x = np.array(x)
    y = np.array(y)
    f1 = np.polyfit(x, y, 13)
    # 13 Fitting to a 13th order polynomial
    p1 = np.poly1d(f1)
    yvals = p1(x)
    return yvals


def ShowDCR(b1, b2, b3, b4, b5, c1, c2, c3, c4, c5, vq1, vq2, vq3, vq4, vq5, bv1, bv2, bv3, bv4, bv5, number):
    x = np.arange(0.1, 2.55, 0.1)
    b1 = [i * 10 ** -3 for i in b1]
    b2 = [i * 10 ** -3 for i in b2]
    b3 = [i * 10 ** -3 for i in b3]
    b4 = [i * 10 ** -3 for i in b4]
    b5 = [i * 10 ** -3 for i in b5]
    plt.figure(figsize=(19.2, 10.8))
    plt.plot(x, b1, color="g", linestyle="-", marker="h", linewidth=1, label="Vquench %s V breakdown is %s V" % (vq1, bv1))
    for x1, y1, y_c1, in zip(x, b1, c1):
        plt.text(x1, y1, str(y_c1), color="g",ha='center', va='bottom', fontsize=7.5)
    plt.plot(x, b2, color="k", linestyle="-", marker=".", linewidth=1, label="Vquench %s V breakdown is %s V " % (vq2, bv2))
    for x2, y2, y_c2, in zip(x, b2, c2):
        plt.text(x2, y2, str(y_c2),color="k", ha='center', va='bottom', fontsize=7.5)
    plt.plot(x, b3, color="b", linestyle="-", marker="s", linewidth=1, label="Vquench %s V  breakdown is %s V" % (vq3, bv3))
    for x3, y3, y_c3, in zip(x, b3, c3):
        plt.text(x3, y3, str(y_c3), color="b", ha='center', va='bottom', fontsize=7.5)
    plt.plot(x, b4, color="y", linestyle="-", marker="*", linewidth=1, label="Vquench %s V breakdown is %s V" % (vq4, bv4))
    for x4, y4, y_c4, in zip(x, b4, c4):
        plt.text(x4, y4, str(y_c4),color="y", ha='center', va='bottom', fontsize=7.5)
    plt.plot(x, b5, color="m", linestyle="-", marker="p", linewidth=1, label="Vquench %s V breakdown is %s V" % (vq5, bv5))
    for x5, y5, y_c5, in zip(x, b5, c5):
        plt.text(x5, y5, str(y_c5),color="m", ha='center', va='bottom', fontsize=7.5)
    plt.legend(loc='upper left', bbox_to_anchor=(0.2, 0.95))
    plt.xlabel('Excess Bias Voltage')
    plt.ylabel('kHz')
    plt.title("dcr,chip %s,100000,output0. oscilloscope: \n 100ms/div,1v/div,offset=0v,trigger 1.8" % (number))
    plt.savefig('chip' + str(number) + 'DCR3.png', dpi=1000)
    plt.show()


def ShowDeadtime(vq1, vq2, ydeadtime1, ydeadtime2, ydeadtime3, vhv1, vhv2, vhv3, number):
    x = np.arange(vq1, vq2 + 0.01, 0.05)
    ydeadtime1 = [i * 10 ** 9 for i in ydeadtime1]
    ydeadtime2 = [i * 10 ** 9 for i in ydeadtime2]
    ydeadtime3 = [i * 10 ** 9 for i in ydeadtime3]
    #y1 = Polyfitting(x, ydeadtime1)
    #y2 = Polyfitting(x, ydeadtime2)
    #y3 = Polyfitting(x, ydeadtime3)
    y1 = ydeadtime1
    y2 = ydeadtime2
    y3 = ydeadtime3
    plt.figure(figsize=(19.2, 10.8))
    plt.plot(x, y1, color="g", linestyle="-", marker="h", linewidth=1, label="VHV=%s V" % (vhv1))
    plt.plot(x, y2, color="k", linestyle="-", marker=".", linewidth=1, label="VHV=%s V" % (vhv2))
    plt.plot(x, y3, color="b", linestyle="-", marker="s", linewidth=1, label="VHV=%s V" % (vhv3))
    plt.legend(loc='upper left', bbox_to_anchor=(0.2, 0.95))
    plt.title("deadtime,chip %s,100000,output0 \n oscilloscope: 50ns/div,1v/div,offset=0v,trigger 1.8" % (number))
    plt.xlabel('Voltage')
    plt.ylabel('time(ns)')
    plt.savefig('chip' + str(number) + 'Deadtime6.png', dpi=1000)
    plt.show()

number = 92

# Keep vhv unchanged, measure the relationship between dcr and vquench
y, y2 = VquenchDCR(0.1)
y = [i * 10 ** -3 for i in y]
x = np.arange(1, 3.05, 0.1)
plt.figure()
plt.plot(x, y, color="g", linestyle="-", marker="h", linewidth=1)
plt.xlabel('vquench(V)')
plt.ylabel('dcr(kHZ)')
plt.title("VHV=16v,chip %s,100000,output0 \n oscilloscope: 100ms/div,1v/div,offset=0v,trigger 1.8" % (number))
plt.savefig('chip' + str(number) + 'dcr&vquench2.png', dpi=600)
plt.show()


# DCR
vq1 = 1
bv1 = BreakdownVoltage(vq1)
b1, c1 = DCR(bv1, vq1, 0.1, 1)
vq2 = 1.5
bv2 = BreakdownVoltage(vq2)
b2, c2 = DCR(bv2, vq2, 0.1, 1)
vq3 = 2
bv3 = BreakdownVoltage(vq3)
b3, c3 = DCR(bv3, vq3, 0.1, 1)
vq4 = 2.5
bv4 = BreakdownVoltage(vq4)
b4, c4 = DCR(bv4, vq4, 0.1, 1)
vq5 = 3
bv5 = BreakdownVoltage(vq5)
b5, c5 = DCR(bv5, vq5, 0.1, 1)
data = np.column_stack((b1,c1,b2,c2,b3,c3,b4,c4,b5,c5))
np.savetxt('chip'+str(number)+'DCR.txt',data)
ShowDCR(b1, b2, b3, b4, b5, c1, c2, c3, c4, c5, vq1, vq2, vq3, vq4, vq5, bv1, bv2, bv3, bv4, bv5, number)

# Deadtime

vq1 = 1.2
vq2 = 2.4
vhv1 = 16.5
vhv2 = 17
vhv3 = 17.5
ydeadtime1 = Deadtime(vq1, vq2, vhv1)
ydeadtime2 = Deadtime(vq1, vq2, vhv2)
ydeadtime3 = Deadtime(vq1, vq2, vhv3)
data = np.column_stack((ydeadtime1,ydeadtime2,ydeadtime3))
np.savetxt('chip'+str(number)+'Deadtime.txt',data)
ShowDeadtime(vq1, vq2, ydeadtime1, ydeadtime2, ydeadtime3, vhv1, vhv2, vhv3, number)


E3647A2.close()
E3647A.close()
scope.close()
plt.show()
rm.close()