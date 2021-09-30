import math
import utm
#import requests
import sys


# 坐标转换变量
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方
R = 6371.004 #地球平均半径,km

#原始utm坐标
shanghai_disney = [[371748.1819410932,3446194.089744417],[371732.21499999997,3446206.74],
                   [371741.32803086017, 3446199.1045242976]]
beijing_huanbao_park = [[428103.1931829389,4435076.623904644],[429546.80000000005,4435058.93],
                        [428483.9780217677,4435094.445732749]]
suzhou_xiangcheng_all = [[273710.0889006674,3478507.697143177],[275077.2508038769, 3478116.6925968286],
                         [276331.828573135, 3477599.6366335545]]
shanghai_auto_expo = [[325100.556601454, 3462264.861553303]]
xiongan_demo = [[405341.97499707027, 4322824.7675331505],[405365.64480820496,4322627.932949567],
                [405379.1623833491,4322713.170005528]]

#由百度api得到的bd09坐标,http://api.map.baidu.com/geoconv/v1/?coords=x,y&from=1&to=5&ak=uolMgmSUAoLergh1sDn8rLAl6HIbxwq6
shanghai_disney_ground_truth = [[121.66533402712196, 31.146666658287729],[121.66516538433759, 31.146775764357135],
                                [121.66526187056945, 31.146709896020075]]
beijing_huanbao_park_gound_truth = [[116.16956284277943, 40.07056408975503],[116.18650150799776,40.070324901516148],
                                    [116.17402093244046, 40.07072646363089]]
suzhou_xiangcheng_all_ground_truth = [[120.63010816289611, 31.42313232633027],[120.64465309101769,31.41962159497558],
                                      [120.65802394850374, 31.41504550887717]]
shanghai_auto_expo_ground_truth = [[121.1737140814689, 31.28563422920602]]
xiongan_demo_ground_truth = [[115.91834045269471, 39.05642589604968],[115.91864176490437, 39.05465668137912],
                             [115.91878509542595, 39.05542762559631]]

def utm_to_bd09(utm_e, utm_n, zone=51, hemi='r'):
    """
    UTM（通用横轴墨卡托）坐标转bd09坐标(百度)
    :param utm_e:
    :param utm_n:
    :param zone:
    :param hemi:
    :return:
    """
    bd_lng = None
    bd_lat = None
    try:
        # utm转gps
        lat, lng = utm.to_latlon(utm_e, utm_n, zone, str(hemi))
        if not out_of_china(lng, lat):  # 判断是否在国内
            bd_lng, bd_lat = wgs84_to_bd09(lng, lat)
        else:
            return lng, lat
    except Exception as e:
        data = str({"utm_e": utm_e, "utm_n": utm_n, 'zone': zone})
    return bd_lng, bd_lat


def utm_to_gcj02(utm_e, utm_n, zone=50, hemi='N'):
    """
    UTM（通用横轴墨卡托）坐标转火星坐标系(GCJ-02)
    UTM-->谷歌、高德
    :param utm_e:
    :param utm_n:
    :param zone:
    :param hemi:
    :return:
    """
    mglng = None
    mglat = None
    try:
        # utm转WGS84(GPS坐标)
        lat, lng = utm.to_latlon(utm_e, utm_n, zone, str(hemi))
        if not out_of_china(lng, lat):  # 判断是否在国内
            mglng, mglat = wgs84_to_gcj02(lng, lat)
    except Exception as e:
        print(e)
    return mglng, mglat


def gcj02_to_utm(lon, lat):
    """
    火星坐标系(GCJ-02)转UTM
    谷歌、高德——>墨卡托
    :param lon:
    :param lat:
    :return:(56.79680,-5.00601)=>(377485.7656709162, 6296561.854853108, 30, 'V')

    """
    lon, lat = gcj02_to_wgs84(lon, lat)
    res_utm = utm.from_latlon(lat, lon)
    return res_utm[0], res_utm[1]


def bd09_to_utm(lon, lat):
    """
    bd09坐标(百度)转UTM
    百度坐标——>墨卡托
    :param lon:
    :param lat:
    :return:(56.79680,-5.00601)=>(377485.7656709162, 6296561.854853108, 30, 'V')

    """
    lon, lat = bd09_to_wgs84(lon, lat)
    res_utm = utm.from_latlon(lat, lon)
    return res_utm[0], res_utm[1]


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    lng = float(lng)
    lat = float(lat)
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lng, bd_lat


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    bd_lat = float(bd_lat)
    bd_lon = float(bd_lon)
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return gg_lng, gg_lat


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    GPS坐标-->谷歌、高德
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return mglng, mglat


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转WGS84
    谷歌、高德-->GPS坐标
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return [lng, lat]
    mglng, mglat = wgs84_to_gcj02(lng, lat)
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转WGS84
    百度-->GPS坐标
    :param bd_lon:
    :param bd_lat:
    :return:
    """
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    """
    WGS84转百度坐标系(BD-09)
    GPS坐标-->百度
    :param lon:
    :param lat:
    :return:
    """
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    WGS84(GPS)坐标的判断是否再国内
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (73.66 < lng < 135.05 and 3.86 < lat < 53.55)


def cal_error(lona, lata, lonb, latb):
    c = math.sin(lata) * math.sin(latb) + math.cos(lata) * math.cos(latb) * math.cos(lona - lonb)
    dist = R*math.acos(c)*pi/180
    print("error:", dist*1000)


def radians(d):
    return d*math.pi/180.0


def cal_error2(lona, lata, lonb, latb):
    lona = radians(lona)
    lata = radians(lata)
    lonb = radians(lonb)
    latb = radians(latb)
    lat = lata - latb
    lon = lona - lonb

    print("error:", 2000 * math.asin(math.sqrt(math.sin(lat / 2) * math.sin(lat / 2) + math.cos(lata) * math.cos(latb) * math.sin(lon / 2) * math.sin(lon / 2))) * 6378.137)


# def get_bd09_by_api(lng, lat):
#     url = "http://api.map.baidu.com/geoconv/v1/"
#     param = {}
#     param['coords'] = str(lng)+','+str(lat)
#     param['from'] = '1'
#     param['to'] = '5'
#     param['ak'] = 'uolMgmSUAoLergh1sDn8rLAl6HIbxwq6'
#     r = requests.get(url, params=param)
#     print(r.content)




utm_zone = int(sys.argv[1])
utm_hemi = str(sys.argv[2])
i = 3
while i < len(sys.argv):
    utm_east = float(sys.argv[i])
    utm_north = float(sys.argv[i + 1])
    code_lng, code_lat = utm_to_bd09(utm_east, utm_north, utm_zone, utm_hemi)
    print(code_lat)
    print(code_lng)
    i = i + 2