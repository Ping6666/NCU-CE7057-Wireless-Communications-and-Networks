import math

# DEBUG
# DEBUG_ = True
DEBUG_ = False


# compute the length of the vector
def VectorLength(vector):
    if type(vector) != list:
        return -1
    tmp = 0
    for i in vector:
        tmp += pow(i, 2)
    return pow(tmp, 1 / 2)


# do dot product for two vector
def DotProduct(v1, v2):
    if type(v1) != list or type(v2) != list:
        return -1
    if len(v1) != len(v2):
        return -2
    tmp = 0
    for i in range(len(v1)):
        tmp += v1[i] * v2[i]
    return tmp


# [Spherical coordinate system - Wikipedia](https://en.wikipedia.org/wiki/Spherical_coordinate_system)
def LatitudeLongitudeCorrection(coordinate):
    if type(coordinate) != list or len(coordinate) != 2:
        return -1
    # φ: Latitude, coordinate[0]; 90 0 -90
    ## no need to change
    # coordinate[0] = coordinate[0]
    # θ: Longitude, coordinate[1]; 180 0 -180
    # transform the Longitude
    coordinate[1] = coordinate[1] % 360
    if coordinate[1] > 180:
        coordinate[1] = -(360 - coordinate[1])
    elif coordinate[1] < -180:
        coordinate[1] = 360 + coordinate[1]
    return coordinate


# Geographic coordinate system <-> Cartesian coordinate system
def GeographicCartesianConvert(coordinate):
    # coordinate must be a list
    if type(coordinate) != list:
        return -1
    if len(coordinate) == 2:  ## Geographic coordinate system
        # (r, θ, φ) but reduce to (θ, φ)
        # φ: Latitude, coordinate[0]
        # θ: Longitude, coordinate[1]
        newCoordinate = [
            math.sin(math.radians(90 - coordinate[0])) *
            math.cos(math.radians(coordinate[1])),
            math.sin(math.radians(90 - coordinate[0])) *
            math.sin(math.radians(coordinate[1])),
            math.cos(math.radians(90 - coordinate[0]))
        ]
        return newCoordinate
    elif len(coordinate) == 3:  ## Cartesian coordinate system
        # (x, y, z)
        r = VectorLength(coordinate)
        newCoordinate = [
            # θ: Latitude, coordinate[0]
            math.degrees(math.acos(coordinate[2] / r)),
            # λ: Longitude, coordinate[1]
            math.degrees(math.atan(coordinate[1] / coordinate[0]))
        ]
        newCoordinate[0] = 90 - newCoordinate[0]
        newCoordinate = LatitudeLongitudeCorrection(newCoordinate)
        # correct the Longitude since the atan has ambiguous value
        if (((coordinate[0] > 0) and (coordinate[1] > 0)
             and not (newCoordinate[1] <= 90 and newCoordinate[1] >= 0)) or
            ((coordinate[0] > 0) and (coordinate[1] < 0)
             and not (newCoordinate[1] >= -90 and newCoordinate[1] <= 0)) or
            ((coordinate[0] < 0) and (coordinate[1] > 0)
             and not (newCoordinate[1] <= 180 and newCoordinate[1] >= 90)) or
            ((coordinate[0] < 0) and (coordinate[1] < 0)
             and not (newCoordinate[1] >= -180 and newCoordinate[1] <= -90))):
            newCoordinate[1] = newCoordinate[1] - 180
        return LatitudeLongitudeCorrection(newCoordinate)
    else:
        return -2


errorRate = 1.25  # 25% error margin


def CircleIntersection(PList, RList, base, checktype):
    checkList = [0, 1, 2]
    # PList = Point List; [A, B, C]; A: list, len 2
    # RLisr = Radius List; [toA, toB, toC]; toA: float / int
    # checktype (no check); 0: A, 1: B, 2: C
    if type(PList) != list or len(PList) != 3:
        if DEBUG_:
            print("CircleIntersection type-1 error.")
        return -1  # type error
    if type(PList[0]) != list or type(PList[1]) != list or type(
            PList[2]) != list:
        if DEBUG_:
            print("CircleIntersection type-2 error.")
        return -2  # type error
    if len(PList[0]) != 2 or len(PList[1]) != 2 or len(PList[2]) != 2:
        if DEBUG_:
            print("CircleIntersection len error.")
        return -3  # len error
    if checktype in checkList:
        checkList.remove(checktype)
    # compute the unit
    RList = [
        RList[0] / base[checktype], RList[1] / base[checktype],
        RList[2] / base[checktype]
    ]
    # point2point vector (B-A)
    Rv = [PList[checkList[1]][j] - PList[checkList[0]][j] for j in range(2)]
    Rv_len = VectorLength(Rv)
    rRv = [-Rv[1], Rv[0]]
    if Rv_len >= RList[checkList[0]] + RList[checkList[1]]:
        if DEBUG_:
            print("CircleIntersection range-1 error.")
        return -4  # range error
    # Xr_len: X point rotate (on the view point) len, not unit or vector
    Xr_len = ((pow(Rv_len, 2) + pow(RList[0], 2) - pow(RList[1], 2)) /
              (2 * Rv_len))
    # Yr_len: same meaning, or said h of the triangle
    # should be +/-, but this will always be +
    Yr_len = pow(pow(RList[0], 2) - pow(Xr_len, 2), 1 / 2)
    if type(Yr_len) == complex:
        Yr_len = Yr_len.real
    if DEBUG_:
        print("CircleIntersection: " + str(PList) + " " + str(RList) + " " +
              str(checktype))
        print("A point: " + str(PList[checkList[0]]))
        print("B point: " + str(PList[checkList[1]]))
        print("BA vector: " + str(Rv) + "; self_len: " + str(Rv_len))
        print("x unit count: " + str(Xr_len) + "; y unit count: " +
              str(Yr_len))
    # Mid intersection point
    Midp = [
        PList[checkList[0]][j] + (Xr_len / Rv_len) * Rv[j] for j in range(2)
    ]
    # Edge intersection point * 2
    Edgep = [[Midp[j] + (Yr_len / Rv_len) * rRv[j] for j in range(2)],
             [Midp[j] - (Yr_len / Rv_len) * rRv[j] for j in range(2)]]
    Edgepv = [[PList[checktype][j] - Edgep[0][j] for j in range(2)],
              [PList[checktype][j] - Edgep[1][j] for j in range(2)]]
    Edgepv_len = [VectorLength(Edgepv[0]), VectorLength(Edgepv[1])]
    if DEBUG_:
        print(str(Edgepv_len[0]) + " " + str(Edgepv_len[1]))
    minLen = min(Edgepv_len[0], Edgepv_len[1])
    if minLen <= RList[checktype] * errorRate:
        if DEBUG_:
            print("Result point: " + str(Edgepv[Edgepv_len.index(minLen)]) +
                  "\n")
        return Edgepv[Edgepv_len.index(minLen)]
    # cheat part
    # return Edgepv[Edgepv_len.index(minLen)]
    # end of cheat part
    if DEBUG_:
        print("CircleIntersection range-2 error.")
    return -5  # range error


def DataInput(a, b, c, base):
    # a, b, c is list and with [Latitude, Longitude, Radius with target (meter)]
    # base: [bc, ac, ab] the length between the point in meter
    if type(a) != list or type(b) != list or type(c) != list:
        if DEBUG_:
            print("DataInput type error.")
        return -1
    if len(a) != 3 or len(b) != 3 or len(c) != 3:
        if DEBUG_:
            print("DataInput len error.")
        return -2
    # T_Pos: Trilateration Posistion in 3D
    T_Pos = [
        GeographicCartesianConvert(a[0:2]),
        GeographicCartesianConvert(b[0:2]),
        GeographicCartesianConvert(c[0:2])
    ]
    # A_point: the base of all (A, B, C)
    A_point = T_Pos[0]
    # Bv: B vector
    Bv = [T_Pos[1][j] - T_Pos[0][j] for j in range(3)]
    Bv_len = VectorLength(Bv)
    # Cv: C vector
    Cv = [T_Pos[2][j] - T_Pos[0][j] for j in range(3)]
    Cv_len = VectorLength(Cv)
    # Cp: C project
    Cp_x = DotProduct(Cv, Bv) / Bv_len
    Cp_y = pow(pow(Cv_len, 2) - pow(Cp_x, 2), 1 / 2)  # Pythagorean theorem
    if DEBUG_:
        print("DataInput: " + str(a) + " " + str(b) + " " + str(c))
        print("A Point: " + str(A_point))
        print("A2B vector: " + str(Bv) + "; self_len: " + str(Bv_len))
        print("A2C vector: " + str(Cv) + "; self_len: " + str(Cv_len))
        print("Ap in 2D: " + str([0, 0]))
        print("Bp in 2D: " + str([1, 0]))
        print("Cp in 2D: " + str([Cp_x / Bv_len, Cp_y / Bv_len]) + "\n")
    # Gp_: Gateway Point List
    Gp_ = [[0, 0], [1, 0], [Cp_x / Bv_len, Cp_y / Bv_len]]
    # reverse Bv on same plane
    rBv = [Cv[j] - ((Cp_x / Bv_len) * Bv[j]) for j in range(3)]
    rBv_len = VectorLength(rBv)
    # Gp_range: the target range between gateway
    Gp_range = [a[2], b[2], c[2]]
    ANS_List = []
    a = CircleIntersection(Gp_, Gp_range, base, 0)
    if type(a) != list:
        if DEBUG_:
            print(a)
    else:
        ANS_List.append(a)
    b = CircleIntersection(Gp_, Gp_range, base, 1)
    if type(b) != list:
        if DEBUG_:
            print(b)
    else:
        ANS_List.append(b)
    c = CircleIntersection(Gp_, Gp_range, base, 2)
    if type(c) != list:
        if DEBUG_:
            print(c)
    else:
        ANS_List.append(c)
    # compute ans
    if len(ANS_List) == 0:
        if DEBUG_:
            print("DataInput call CircleIntersection ans error.")
        return -3
    ANS_ = [0, 0]
    for item in ANS_List:
        ANS_[0] = item[0]
        ANS_[1] = item[1]
    ANS_[0] /= len(ANS_List)
    ANS_[1] /= len(ANS_List)
    # remove div. Bv_len and rBv_len
    ANSp = [
        A_point[j] + (ANS_[0] * Bv[j]) + (ANS_[1] * rBv[j]) for j in range(3)
    ]
    ANS_geo = GeographicCartesianConvert(ANSp)
    if DEBUG_:
        print("ANS in 2D: " + str(ANS_))
        print("ANS in 3D: " + str(ANSp))
        print("ANS in geo: " + str(ANS_geo))
    return ANS_geo
