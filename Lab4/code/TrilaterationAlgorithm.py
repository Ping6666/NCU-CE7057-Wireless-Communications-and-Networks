import math


class Vector:
    vector = []

    def __new__(cls, *args, **kwargs):
        if len(args) != 1:
            return -1  # args length error
        if type(args[0]) != list or len(args[0]) == 0:
            return -2  # arg[0]: Point_pos_ type or length error
        return super(Vector, cls).__new__(cls)

    def __init__(self, vector_):
        self.vector = vector_
        return

    def Length(self):
        if type(self) != Vector:
            self = Vector(self)
        tmp = 0
        for i in self.vector:
            tmp += pow(i, 2)
        return pow(tmp, 1 / 2)

    def Add(self, v1, multiplier=1):
        if type(self) != Vector:
            self = Vector(self)
        if (type(v1) != list or len(v1) != len(self.vector)
                or (type(multiplier) != int and type(multiplier) != float)):
            return -1
        Add_result = [
            self.vector[i] + multiplier * v1[i]
            for i in range(len(self.vector))
        ]
        return Add_result

    def DotProduct(self, v1):
        if type(self) != Vector:
            self = Vector(self)
        if type(v1) != list or len(v1) != len(self.vector):
            return -1
        tmp = 0
        for i in range(len(self.vector)):
            tmp += self.vector[i] * v1[i]
        return tmp


class Location:
    GPS_pos = []
    GPS_point = []

    def __new__(cls, GPS_pos_=[], GPS_point_=[]):
        if type(GPS_pos_) != list or type(GPS_point_) != list:
            return -1  # type error
        if len(GPS_pos_) != 2 and len(GPS_point_) != 3:
            return -2  # length error
        return super(Location, cls).__new__(cls)

    def __init__(self, GPS_pos_=[], GPS_point_=[]):
        self.GPS_pos = GPS_pos_
        self.GPS_point = GPS_point_
        self.GPS_Correction()
        self.GPS_Convert()
        return

    def GPS_Correction(self):
        # Latitude and Longitude correction
        # GPS_pos = [φ, θ]
        # φ:  Latitude, coordinate[0];  90 0 -90   ## no need to change
        # θ: Longitude, coordinate[1]; 180 0 -180  ## need to transform
        if len(self.GPS_pos) == 2:
            self.GPS_pos[1] = self.GPS_pos[1] % 360
            if self.GPS_pos[1] > 180:
                self.GPS_pos[1] = -(360 - self.GPS_pos[1])
            elif self.GPS_pos[1] < -180:
                self.GPS_pos[1] = 360 + self.GPS_pos[1]
        else:
            self.GPS_pos = []
        return

    def GPS_Convert(self, set_=0):
        if type(self) != Location:
            if type(self) == list and len(self) == 2:
                self = Location(GPS_pos_=self)
            elif type(self) == list and len(self) == 3:
                self = Location(GPS_point_=self)
        # Geographic coordinate system <-> Cartesian coordinate system
        if len(self.GPS_pos) == 0 and len(self.GPS_point) == 0:
            print("please init Location first")
            return -1  # return false
        if (len(self.GPS_point) == 0
                or set_ == 2):  ## Geographic coordinate system
            # (r, θ, φ) but reduce to (θ, φ)
            # φ:  Latitude, GPS_pos[0]
            # θ: Longitude, GPS_pos[1]
            self.GPS_point = [
                math.sin(math.radians(90 - self.GPS_pos[0])) *
                math.cos(math.radians(self.GPS_pos[1])),
                math.sin(math.radians(90 - self.GPS_pos[0])) *
                math.sin(math.radians(self.GPS_pos[1])),
                math.cos(math.radians(90 - self.GPS_pos[0]))
            ]
            return 1  # set GPS_point
        elif (len(self.GPS_pos) == 0
              or set_ == 1):  ## Cartesian coordinate system
            # (x, y, z)
            # θ:  Latitude, self.GPS_point[0]
            # λ: Longitude, self.GPS_point[1]
            r = Vector.Length(Vector(self.GPS_point))
            self.GPS_pos = [
                math.degrees(math.acos(self.GPS_point[2] / r)),
                math.degrees(math.atan(self.GPS_point[1] / self.GPS_point[0]))
            ]
            # correct the Latitude
            self.GPS_pos[0] = 90 - self.GPS_pos[0]
            self.GPS_Correction()
            # correct the Longitude since the atan has ambiguous value
            if (((self.GPS_point[0] > 0) and (self.GPS_point[1] > 0)
                 and not (self.GPS_pos[1] <= 90 and self.GPS_pos[1] >= 0)) or
                ((self.GPS_point[0] > 0) and (self.GPS_point[1] < 0)
                 and not (self.GPS_pos[1] >= -90 and self.GPS_pos[1] <= 0)) or
                ((self.GPS_point[0] < 0) and (self.GPS_point[1] > 0)
                 and not (self.GPS_pos[1] <= 180 and self.GPS_pos[1] >= 90)) or
                ((self.GPS_point[0] < 0) and (self.GPS_point[1] < 0) and
                 not (self.GPS_pos[1] >= -180 and self.GPS_pos[1] <= -90))):
                self.GPS_pos[1] = self.GPS_pos[1] - 180
            self.GPS_Correction()
            return 2  # set GPS_pos
        else:
            return 0  # did not set anything


# check the valid ans that is inside the three point
# therefore, if the point is outside, then it will return error
def CircleIntersection(Point_, Radius_, Base_, Check_, Boundary_):
    # Point_: point list, each item was a list and with len equal to two
    # Radius_: radius list, each item was a float or int, len equal to Point_
    # Base_: base list, each item was also a float or int. this is for the perspective of vector
    # Check_: check list, must be two int and less then the len of Point_
    # Boundary_: check the valid side of intersection and radius check
    if (type(Point_) != list or type(Radius_) != list or type(Base_) != list
            or type(Check_) != list):
        return -1  # input type error
    elif (len(Point_) != len(Radius_) or len(Point_) != len(Base_)
          or len(Check_) != 2):
        return -2  # input list length error
    elif ((Check_[0] >= len(Point_) or Check_[1] >= len(Point_)
           or Boundary_ >= len(Point_))
          or (type(Check_[0]) != int or type(Check_[1]) != int
              or type(Boundary_) != int)):
        return -3  # input check list length error or type error
    elif len(Point_[Check_[0]]) != 2 or len(Point_[Check_[1]]) != 2:
        return -4  # input point list length error
    # -- Pre_func type check FIN --
    # compute the unit
    Radius_ = Vector.Add(([0] * len(Radius_)), Radius_, (1 / Base_[Boundary_]))
    # Rv: point2point vector
    Rv = Vector.Add(Point_[Check_[1]], Point_[Check_[0]], -1)
    Rv_len = Vector.Length(Rv)
    rRv = [-Rv[1], Rv[0]]  # the normal vector in 2D
    if Rv_len >= Radius_[Check_[0]] + Radius_[Check_[1]]:
        return -11  # radius check fail two circle may have no intersection or only have one
    # Xr_len: X point rotate (on the view point) len, not unit or vector
    Xr_len = ((pow(Rv_len, 2) + pow(Radius_[0], 2) - pow(Radius_[1], 2)) /
              (2 * Rv_len))  # Pythagorean theorem
    # Yr_len: same meaning, or said h of the triangle. should be +/-, but this will always be +
    Yr_len = (pow(pow(Radius_[0], 2) - pow(Xr_len, 2),
                  1 / 2))  # Pythagorean theorem
    if type(Yr_len) == complex:
        Yr_len = Yr_len.real
        # return -12  # radius compute result have image part
    # Mid intersection point
    Mp = Vector.Add(Point_[Check_[0]], Rv, (Xr_len / Rv_len))
    # Edge intersection point * 2 (+/-)
    Ep = [
        Vector.Add(Mp, rRv, (Yr_len / Rv_len)),
        Vector.Add(Mp, rRv, -(Yr_len / Rv_len))
    ]
    Epv = [
        Vector.Add(Point_[Boundary_], Ep[0], -1),
        Vector.Add(Point_[Boundary_], Ep[1], -1)
    ]
    Epv_len = [Vector.Length(Epv[0]), Vector.Length(Epv[1])]  # list
    min_Epv_len = min(Epv_len[0], Epv_len[1])
    if min_Epv_len <= Radius_[Boundary_] * 1.25:
        return Epv[Epv_len.index(min_Epv_len)]
    return -21  # error, the point is not inside three point


def DataInput(a, b, c, base):
    # a, b, c is list and with [Latitude, Longitude, Radius with target (meter)]
    # base: [bc, ac, ab] the length between the point in meter
    if (type(a) != list or type(b) != list or type(c) != list
            or type(base) != list):
        return -1  # input type error
    if len(a) != 3 or len(b) != 3 or len(c) != 3:
        return -2  # input length error
    # T_Pos: Trilateration Posistion in 3D
    T_Pos = [
        Location(a[0:2]).GPS_point,
        Location(b[0:2]).GPS_point,
        Location(c[0:2]).GPS_point
    ]
    # A_point: the base of all (A, B, C)
    A_point = T_Pos[0]
    # Bv: B vector
    Bv = Vector.Add(T_Pos[1], T_Pos[0], -1)
    Bv_len = Vector.Length(Bv)
    # Cv: C vector
    Cv = Vector.Add(T_Pos[2], T_Pos[0], -1)
    Cv_len = Vector.Length(Cv)
    # Cp: C project
    Cp_x = Vector.DotProduct(Cv, Bv) / Bv_len
    Cp_y = pow(pow(Cv_len, 2) - pow(Cp_x, 2), 1 / 2)  # Pythagorean theorem
    # Gp_: Gateway Point List
    Gp_ = [[0, 0], [1, 0], [Cp_x / Bv_len, Cp_y / Bv_len]]
    # reverse Bv on same plane
    rBv = Vector.Add(Cv, Bv, -(Cp_x / Bv_len))
    rBv_len = Vector.Length(rBv)
    # Gp_range: the target range between gateway
    Gp_range = [a[2], b[2], c[2]]
    all_ = [0, 1, 2]
    ANS_List = [
        CircleIntersection(Gp_, Gp_range, base, [j for j in all_ if j != i], i)
        for i in range(3)
    ]
    ANS_List = [j for j in ANS_List if type(j) == list]
    # compute ans
    if len(ANS_List) == 0:
        return -3
    ANS_ = Vector([0, 0])
    for item in ANS_List:
        ANS_ = Vector.Add(ANS_, item)
    ANS_ = Vector.Add([0] * len(ANS_), ANS_, 1 / len(ANS_List))
    # remove div. Bv_len and rBv_len
    ANSp = Vector.Add(A_point, Bv, ANS_[0])
    ANSp = Vector.Add(ANSp, rBv, ANS_[1])
    ANS_geo = Location(GPS_point_=ANSp).GPS_pos
    return ANS_geo


def mainFunc():
    print("Test")
    return


if __name__ == '__main__':
    mainFunc()
