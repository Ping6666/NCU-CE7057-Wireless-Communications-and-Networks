import sys, os, json
import pandas as pd
import numpy as np

from TrilaterationAlgorithm import DataInput

## Reference Website:
# [lora測試實驗地點 - Google 我的地圖](https://www.google.com/maps/d/viewer?mid=1Kn1r0J6jdb6VR1tRXt7dIrJN3LA&ll=24.969030075612043%2C121.19055535&z=17)
# [Best JSON Parser Online](https://jsonformatter.org/json-parser)
# [經緯度距離計算](https://www4.hhlink.com/%E7%B6%93%E7%B7%AF%E5%BA%A6)

# dstMAC_List: gateway 1~3
dstMAC_List = [
    '00800000a000151a', '00800000a0000a1c', '00800000a0000ed1',
    '00800000a00006d4'
]
dstMAC_gps_List = [[24.96715, 121.18766], [24.96822, 121.19437],
                   [24.97154, 121.19268], [24.96715, 121.18766]]
# srcLoc_List: location as the list
# srcLoc_List = ['123']
srcLoc_List = ['2131231', '2', '3', '4', '6', '7', '8', '9', '10', '11', '29']
# srcLoc_List = ['2', '3', '4', '6', '7', '8', '9', '10', '11', '29']

## disMAC loc list
# gateway 1: 24.96715, 121.18766 (00800000a000151a)
# gateway 2: 24.96822, 121.19437 (00800000a0000a1c)
# gateway 3: 24.97154, 121.19268 (00800000a0000ed1)
# gateway 4: 24.96715, 121.18766 (00800000a00006d4) (same as gateway 1)

## -- the target GPS pos --
target_gps_loc = [24.96693, 121.18730]
# loc 123: 24.96693, 121.18730
# -- the target GPS pos --

## srcLoc list
# loc  2: 24.96733, 121.18701
# loc  3: 24.96747, 121.18715
# loc  4: 24.96729, 121.18728
# loc  6: 24.96756, 121.18768
# loc  7: 24.96749, 121.18794
# loc  8: 24.96746, 121.18802
# loc  9: 24.96744, 121.18837
# loc 10: 24.96738, 121.18859
# loc 11: 24.96745, 121.18874
# loc 29: 24.96667, 121.18784

# distance_List: take out with (srcLoc, dstMAC)
dis_List = [[44, 726, 746, 44], [68, 748, 739, 0], [63, 732, 718, 0],
            [41, 722, 721, 0], [46, 678, 670, 0], [47, 653, 656, 0],
            [50, 645, 653, 0], [78, 611, 630, 0], [97, 590, 619, 0],
            [114, 573, 604, 0], [57, 680, 729, 0]]  # in m
# dis_List = [[0.044, 0.726, 0.746, 0.044]]  # in km
# dis_List = [[0.068, 0.748, 0.739], [0.063, 0.732, 0.718],
#             [0.041, 0.722, 0.721], [0.046, 0.678, 0.67], [0.047, 0.653, 0.656],
#             [0.05, 0.645, 0.653], [0.078, 0.611, 0.63], [0.097, 0.59, 0.619],
#             [0.114, 0.573, 0.604], [0.057, 0.68, 0.729]]

# dis. dup. 0.653

# gateway_dis: gateway distance: BC, AC, AB
gateway_dis = [406, 703, 686]

# A: 發射端和接收端相隔1米時的訊號強度
AList = [90, 86, 83, 90]
# n: 環境衰減因子
nList = [3, 1.3, 1.7, 3]


def processPATH(pathBase='./testData', fileType='.txt'):
    fileList = []
    for dirPath, dirNames, fileNames in os.walk(pathBase):
        for i, f in enumerate(fileNames):
            if fileType in f:
                newFilePath = os.path.join(dirPath, f)
                fileList.append(newFilePath)
    return fileList


def openFILE(inputFilePath):
    try:
        fd = open(inputFilePath, 'r', encoding='utf-8')
    except:
        print("No such file or directory : " + inputFilePath)
        exit()

    ansList = []

    # file name
    ansList = ansList + inputFilePath.replace('.txt', '').split('_')[2:]

    fileContent = fd.read()
    fd.close()

    fileContent = json.loads(fileContent)

    # object -> result -> uplinkFrames
    ## txInfo
    ansList = ansList + [
        list(fileContent['result']['uplinkFrames'][0]['txInfo'].values())[0]
    ]
    ansList = ansList + list(
        list(fileContent['result']['uplinkFrames'][0]['txInfo'].values())
        [1].values())
    ansList = ansList + [
        list(fileContent['result']['uplinkFrames'][0]['txInfo'].values())[2]
    ]

    ## rxInfo
    for i in range(len(fileContent['result']['uplinkFrames'][0]['rxInfo'])):
        ansList = ansList + list(
            fileContent['result']['uplinkFrames'][0]['rxInfo'][i].values())

    ## phyPayloadJSON
    ## -- just pass for now --

    return ansList


def appendDefaultList(index=0, withLoc=0):
    tmp = 0
    if index == 1:
        tmp = index + withLoc
    theMainList = [[
        'filename-place', 'filename-power', 'filename-spreadfactor',
        'filename-testcount', 'txInfo-frequency', 'txInfo-dataRate-modulation',
        'txInfo-dataRate-bandwidth', 'txInfo-dataRate-spreadFactor',
        'txInfo-dataRate-bitrate', 'txInfo-codeRate', 'rxInfo-mac',
        'rxInfo-time', 'rxInfo-timeSinceGPSEpoch', 'rxInfo-timestamp',
        'rxInfo-rssi', 'rxInfo-loRaSNR', 'rxInfo-board', 'rxInfo-antenna'
    ], ['power_spreadfactor', 'distance', 'rssi', 'loRaSNR'],
                   [
                       'power_sf', 'src_place_id', 'dst_place_id', 'distance',
                       'rssi', 'loRaSNR'
                   ], ['power_sf', 'distance', 'rssi'],
                   ['power_sf', 'distance', 'loRaSNR']]

    return theMainList[tmp]


def distanceCalculator(srcLoc, dstMAC):
    # srcLoc: self location, dstMAC: center mac addr.
    # print(dstMAC)

    try:
        dstMAC_index = dstMAC_List.index(dstMAC)
    except:
        print("\tunexpect search in list. dstMAC:" + dstMAC)
        return -1
    try:
        srcLoc_index = srcLoc_List.index(srcLoc)
    except:
        print("\tunexpect search in list. srcLoc:" + srcLoc)
        return -2

    # range check (seems this is no need)
    if dstMAC_index < 0 or dstMAC_index >= len(dstMAC_List):
        print("\tdst MAC find error.")
        return -1
    elif srcLoc_index < 0 or srcLoc_index >= len(srcLoc_List):
        print("\tsrc loc find error.")
        return -2

    # find in the list and check list if poison
    resultDst = dis_List[srcLoc_index][dstMAC_index]
    if resultDst >= 0:
        return [srcLoc_index, dstMAC_index, resultDst]
    print("\tlist is poison.")
    return -3


def CSVgen(nowRecord, withLoc=0):
    # setting the result list
    str_power_spreadfactor = nowRecord[1] + '_' + nowRecord[2]
    tmp_List_concatenate = [str_power_spreadfactor]
    # loop check all rxInfo
    index = 10
    while index < len(nowRecord):
        tmp_List = distanceCalculator(str(nowRecord[0]), str(nowRecord[index]))
        if type(tmp_List) == list:
            tmp_ = []
            if withLoc != 0:  # with loc
                tmp_ = tmp_List + nowRecord[index + 4:index + 6]
            else:  # without loc
                tmp_ = [tmp_List[2]] + nowRecord[index + 4:index + 6]
            tmp_List_concatenate = tmp_List_concatenate + tmp_
        index += 8
    # print(tmp_List_concatenate)
    return tmp_List_concatenate


def CSVshrink(theResultList, check=0, withLoc=0):
    theANSList = []
    theANSList.append(appendDefaultList(1, withLoc))
    # remove the title
    theResultList.pop(0)
    if check == 0:
        for nowRecord in theResultList:
            ## shrink ver.
            tmp_ = CSVgen(nowRecord, withLoc)
            badCheck, index = 0, -1
            # find in the list
            for i, tmp in enumerate(theANSList):
                if tmp_[0] == tmp[0]:
                    badCheck = 1
                    index = i
            # merge the list
            if badCheck == 1 and index != -1:
                theANSList[index] = theANSList[index] + tmp_[1:]
            else:
                theANSList.append(tmp_)
    else:
        for nowRecord in theResultList:
            ## nor. ver. (with 400 row)
            theANSList.append(CSVgen(nowRecord, withLoc))

    return theANSList


def CSVprocess(theList):  # withLoc = 1
    returnList = []
    theList.pop(0)
    title = appendDefaultList(1, 1)
    returnList.append([title[0]] + title[2:-1])
    for list_ in theList:
        disList_ = []
        i, tmp_returnList = 0, []
        counter = 0
        while True:
            if i >= len(list_):
                break
            if i == 0:
                # add the subtitle
                tmp_returnList = [list_[i]]
                i += 1
            # print("i", i)
            # disList_[id] = power_sf, rssi
            # the json must have three gateway's data
            tmp_ = []
            for j in range(4):
                if i + j * 5 + 3 >= len(list_):
                    print("\tjson is poison!!!\n")
                    break  # skip this data set
                # dst_place, distance, rssi
                tmp_ += [
                    list_[i + j * 5 + 1], list_[i + j * 5 + 2],
                    list_[i + j * 5 + 3]
                ]
            disList_.append(tmp_)
            # print(disList_)
            # shift to the next data set
            i += (4 * 5)  # len
            counter += 1
        for dis in disList_:
            returnList.append(tmp_returnList + dis)
    return returnList


factor = 100
# d unit is 100 meters
# then, Latitude 1 degress is near 111.2 km = 111,200 m


def RSSItoDistance(theList):
    theList.pop(0)
    totalANS = []
    print("\n")
    for num, list_ in enumerate(theList):
        disNow_ = []
        for i in range(4):  # len
            # +0 no shift (id), +1 remove title, +2 shift to rssi
            id_, RSSI = list_[i * 3 + 0 + 1], list_[i * 3 + 2 + 1]
            # print(id_, RSSI)
            # print(int(RSSI))
            # print(AList[id_])
            # print(nList[id_])
            # print(((abs(int(RSSI)) - AList[id_]) / (10 * nList[id_])))
            disNow = factor * pow(10, ((abs(int(RSSI)) - AList[id_]) /
                                       (10 * nList[id_])))
            disNow_.append(disNow)
        # power_sf, dst_place, distance, RSSItoDistance, rssi
        theList[num] = [theList[num][0]] + [
            theList[num][j * 3 + 1:j * 3 + 3] + [item] +
            [theList[num][j * 3 + 3]] for (j, item) in enumerate(disNow_)
        ]
        # print(theList[num])
        tmp_index, tmpList = 0, [[], [], []]
        for i in range(5):
            if i == 0:  # title
                continue
            if theList[num][i][0] == 3:  # invalid gateway
                continue
            tmpList[tmp_index] = dstMAC_gps_List[theList[num][i][0]] + [
                theList[num][i][2]
            ]
            tmp_index += 1
        ansGPS = DataInput(tmpList[0], tmpList[1], tmpList[2], gateway_dis)
        if type(ansGPS) != list:
            print("\tBad thing happened when calling DataInput")
        else:
            print("\tEstimate target GPS: " + str(ansGPS))
            totalANS.append(ansGPS)
    totalANS.append([])
    totalANS.append(target_gps_loc)
    print("\tReal target GPS: " + str(target_gps_loc))
    print("\n")
    return totalANS


def CSVpostProcess(theList):
    # list 1
    list_1 = theList[0:len(theList):2]
    checker = []
    fillList_1 = [[0] * 50] * 8

    ansList_1 = []
    for index, line in enumerate(list_1):
        i = 0
        while True:
            if i >= len(line):
                break
            if i == 0:
                ansList_1.append([line[i]])
                i += 1
                continue
            # print(i)
            if line[i] not in checker:
                checker.append(line[i])
            id_ = checker.index(line[i])
            fillList_1[index][id_] = line[i + 1]
            i += 2
        ansList_1[index] = ansList_1[index] + fillList_1[index]
    checker_1 = ['rssi'] + checker
    ansList_1 = np.array(ansList_1)
    ansList_1 = ansList_1[:, 0:len(checker_1)]
    ansList_1 = ansList_1.tolist()
    ansList_1 = [checker_1] + ansList_1

    # list 2
    list_2 = theList[1:len(theList):2]
    # checker = []
    fillList_2 = [[0] * 50] * 8

    ansList_2 = []
    for index, line in enumerate(list_2):
        i = 0
        while True:
            if i >= len(line):
                break
            if i == 0:
                ansList_2.append([line[i]])
                i += 1
                continue
            # print(i)
            if line[i] not in checker:
                checker.append(line[i])
            id_ = checker.index(line[i])
            fillList_2[index][id_] = line[i + 1]
            i += 2
        ansList_2[index] = ansList_2[index] + fillList_2[index]
    checker = ['snr'] + checker
    ansList_2 = np.array(ansList_2)
    ansList_2 = ansList_2[:, 0:len(checker)]
    ansList_2 = ansList_2.tolist()
    ansList_2 = [checker] + ansList_2
    ansList = ansList_1 + [''] + ansList_2
    return ansList


def main(argv):
    ## preProcess
    print('preProcess')
    theResultList = []
    # take out all the file in the base path
    totalFileList = processPATH()
    # append the list title
    theResultList.append(appendDefaultList())
    # append the list content
    for filePath in totalFileList:
        theResultList.append(openFILE(filePath))
    # print(theResultList)

    ## preProcess - csv gen. (half)
    print('preProcess - csv gen.')
    # save to csv (this is just a half ans)

    #
    df_1 = pd.DataFrame(theResultList)
    df_1.to_csv('halfANS_group3.csv')
    #

    ## postProcess - gen. shrink process
    print('postProcess')
    # theANSList = CSVshrink(theResultList, check=1, withLoc=1)
    theANSList = CSVshrink(theResultList, withLoc=1)

    #
    df_4 = pd.DataFrame(theANSList)
    df_4.to_csv('test1ANS_group3.csv')
    #

    theANSList = CSVprocess(theANSList)

    #
    df_3 = pd.DataFrame(theANSList)
    df_3.to_csv('test2ANS_group3.csv')
    #

    theANSList = RSSItoDistance(theANSList)

    # theANSList = CSVpostProcess(theANSList)

    ## postProcess - csv gen. (final)
    print('postProcess - csv gen.')
    df_2 = pd.DataFrame(theANSList)
    df_2.to_csv('finalANS_group3.csv')

    print('finish!!!')

    return


if __name__ == '__main__':
    # clearScreen()
    main(sys.argv[1:])
    exit()
