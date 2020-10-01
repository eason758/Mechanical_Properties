import csv
import xlrd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def integral(x,y):
    sum = 0
    for i in range(len(x)):
        if i == 0:
            continue
        else:
            sum +=(y[i]+y[i-1])*(x[i]-x[i-1])/2
    return sum


def found_intersection(strain_, stress_, slope_, offset_):
    i = 0
    tmp = i
    flag = False
    for s in strain_:
        if slope_ * (s - offset_) > stress_[i]:
            if not flag:
                tmp = i
                flag = True
        else:
            flag = False
        i += 1
    return tmp, (tmp - 1)

def get_file():

    file = ""
    while not file.endswith('.csv'):
        file = input("Plz give a data file (Full file path, "
                         "and must be .csv file (file name end with '.csv') :\n")

    try:
        _f = open(file, "r")
        return _f
    except:
        return get_file()


def UTS_cal_and_plot(stress_, strain_):
    plt.plot(strain_, stress_)
    plt.plot(strain_[-1], stress_[-1], 'ro')


if __name__ == '__main__':

    print("\n\n                              Wellcom to my program!\n\n")

    f = get_file()
    data = csv.reader(f)

    headers = next(data)

    while True:
        try:
            offset_percentage = float(input("\nOffset_percentage : _____% (not exceed 10%)\n"))
            break
        except:
            print("Only number!")
    while True:
        try:

            print("\nOriginal length x width x height of specimen (cm):")
            speci_len = float(input("length(cm): \n"))
            speci_wid = float(input("\nwidth(cm): \n"))
            speci_hei = float(input("\nOriginal length(cm): \n"))
            break
        except:
            print("Only number!")
    while True:
        try:
            YS_range = int(input("\nPlz give YS data range(first _____th data):\n"
                                 "(115 is recommended)\n"))
            break
        except:
            print("Only number!")

    eng_strain = []
    eng_stress = []

    for row in data:
        eng_strain.append(np.round((float(row[0]) / (speci_hei) * 100),decimals=5))
        eng_stress.append(np.round(float(row[1])/(speci_len*speci_wid*100),decimals=5))

    eng_UTS_stress = max(eng_stress)
    eng_UTS_index = eng_stress.index(max(eng_stress))
    eng_UTS_strain = eng_strain[eng_UTS_index]
    FTP_stress = eng_stress[-1]
    FTP_strain = eng_strain[-1]

    plt.figure(figsize=(12, 8))
    plt.subplots_adjust(right=0.8)
    plt.subplots_adjust(top=0.93)
    plt.subplots_adjust(bottom=0.06)
    plt.subplot(2, 1, 1)
    plt.xlabel("strain(%)")
    plt.ylabel("stress(MPa)")

    plt.title('Stress-strain plot')
    l1_1, = plt.plot(eng_strain, eng_stress)

    offset = offset_percentage

    s = 0

    for x in range(YS_range):
        s += (eng_stress[x + 1] - eng_stress[x]) / (eng_strain[x + 1] - eng_strain[x])

    slope = s / YS_range
    x_max = 0
    while slope * (x_max - offset) < eng_UTS_stress:
        x_max += 0.01

    slope_x = np.round(np.arange(offset, x_max, 0.00001), decimals=5)
    slope_y = np.round(slope * (slope_x - offset), decimals=5)
    l1_2, = plt.plot(slope_x, slope_y)

    (upper, lower) = found_intersection(eng_strain, eng_stress, slope, offset)
    YSP_x = (-((eng_stress[upper] - eng_stress[lower]) / (eng_strain[upper] - eng_strain[lower])) * eng_strain[lower] + eng_stress[lower]
             + (slope * offset))/(slope - ((eng_stress[upper] - eng_stress[lower]) / (eng_strain[upper] - eng_strain[lower])))
    YSP_y = slope * (YSP_x - offset)






    plt.plot(eng_UTS_strain, eng_UTS_stress, 'ro')
    plt.annotate('UTS:(%s, %s)' % (eng_UTS_strain, eng_UTS_stress), xy=(eng_UTS_strain, eng_UTS_stress),
                 xytext=(-100, -30), textcoords='offset pixels')

    plt.plot(FTP_strain, FTP_stress, 'ro')
    plt.annotate('FTP:(%s, %s)' % (FTP_strain, FTP_stress), xy=(FTP_strain, FTP_stress),
                 xytext=(-200, -20), textcoords='offset pixels')

    plt.plot(YSP_x, YSP_y, 'ro')
    plt.annotate('OYS:(%.5f, %.5f)' % (YSP_x, YSP_y), xy=(YSP_x, YSP_y),
                 xytext=(10, -10), textcoords='offset pixels')
    # elastic region
    plt.fill_between(eng_strain[:upper], eng_stress[:upper], color='blue', alpha=0.2)
    A = integral(eng_strain[:upper], eng_stress[:upper])
    # plastic region
    plt.fill_between(eng_strain, eng_stress, color='gray', alpha=0.2)
    B = integral(eng_strain, eng_stress)
    # necking region
    plt.fill_between(eng_strain[eng_UTS_index:], eng_stress[eng_UTS_index:], color='green', alpha=0.2)
    C = integral(eng_strain[eng_UTS_index:], eng_stress[eng_UTS_index:])
    print("A : ", A," B : ",B-A-C," C : ",C)

    plt.text(eng_strain[upper] / 2, eng_stress[upper]/4, 'A', fontsize=13)
    plt.text((eng_strain[upper] + eng_UTS_strain) / 2, eng_stress[upper] / 4,
             'B', fontsize=13)
    plt.text((eng_UTS_strain + FTP_strain) / 2, eng_stress[upper] / 4,
             'C', fontsize=13)

    plt.legend(handles=[l1_1, l1_2], labels=['engineering-\n'
                                             'stress-strain',
                                             'elastic slope'], loc='upper left')

    plt.text(FTP_strain + 5, eng_UTS_stress, 'elastic region : A\n'
                        'plastic region : \nA+B+C\n'
                        'necking region : C\n'
                        'uniform elongation \nregion : A+B',
             verticalalignment='top',
             fontsize=13)

    plt.subplot(2,1, 2)

    plt.xlabel("strain(%)")
    plt.ylabel("stress(Mpa)")

    real_stress = []
    real_strain = []
    for x in eng_strain:
        real_strain.append(np.round(np.log(1 + x/100), decimals=5)*100)
    i = 0
    for x in eng_strain:
        real_stress.append(np.round(eng_stress[i]*(1 + x/100), decimals=5))
        i += 1

    eng_stress = eng_stress[:eng_UTS_index]
    eng_strain = eng_strain[:eng_UTS_index]
    real_UTS_index = real_stress.index(max(real_stress))
    real_stress = real_stress[:real_UTS_index]
    real_strain = real_strain[:real_UTS_index]



    l2_1, = plt.plot(eng_strain, eng_stress)
    plt.plot(eng_strain[-1], eng_stress[-1], 'ro')

    plt.annotate('        Engineering-stress-strain\n'
                 'UTS:(%s, %s)' % (eng_strain[-1], eng_stress[-1]), xy=(eng_strain[-1], eng_stress[-1]),
                 xytext=(-160, 10),textcoords='offset pixels')


    l2_2 = plt.plot(real_strain, real_stress)
    plt.plot(real_strain[-1], real_stress[-1], 'ro')

    plt.annotate('                  True-stress-strain\n'
                 'UTS:(%s, %s)' % (real_strain[-1], real_stress[-1]), xy=(real_strain[-1], real_stress[-1]),
                 xytext=(-170, -40),textcoords='offset pixels')

    plt.legend(handles=[l2_1, l1_2], labels=['engineering-\n'
                                             'stress-strain',
                                             'real-\n'
                                             'stress-strain'], loc='upper left')


    plt.show()

    f.close()
