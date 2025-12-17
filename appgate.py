import math


class Runway:
    def __init__(self, elev: float, rdh: float = 15.0):
        self.elev = elev      # 跑道入口标高(m)
        self.rdh = rdh        # 跑道基准高(m)


class Approach:
    def __init__(self, theta: float = 3.0, d: float = 2.0):
        self.theta = theta    # 下滑角(deg)
        self.d = d            # 冗余距离(km)

    def appgate(self, h: float, runway: Runway) -> float:
        """
        :param h: 航空器高度(m)
        :return: 进近门距离(km)
        """
        delta_h = h - (runway.elev + runway.rdh)
        if delta_h <= 0:
            return 0.0
        return (delta_h / math.tan(math.radians(self.theta))) / 1000 + self.d

    def altitude(self, dist: float, runway: Runway) -> float:
        """
        计算下滑道高度
        :param dist: 离跑道入口距离(km)
        :param runway: Runway对象
        :return: 高度(m)
        """
        dist = max(0.0, dist)
        return (runway.elev + runway.rdh) + math.tan(math.radians(self.theta)) * dist * 1000.0

    def distance_on_glide(self, h: float, runway: Runway) -> float:
        delta_h = h - (runway.elev + runway.rdh)
        if delta_h <= 0:
            return 0.0
        return (delta_h / math.tan(math.radians(self.theta))) / 1000.0