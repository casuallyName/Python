import cv2
import numpy as np
from numpy.linalg import norm
import os
import json
import time


class StatModel(object):
    def load(self, fn):
        self.model = self.model.load(fn)

    def save(self, fn):
        self.model.save(fn)


class SVM(StatModel):
    def __init__(self, C=1, gamma=0.5):
        self.model = cv2.ml.SVM_create()
        self.model.setGamma(gamma)
        self.model.setC(C)
        self.model.setKernel(cv2.ml.SVM_RBF)
        self.model.setType(cv2.ml.SVM_C_SVC)
        # 不能保证包括所有省份

    # 训练svm
    def train(self, samples, responses):
        self.model.train(samples, cv2.ml.ROW_SAMPLE, responses)

    # 字符识别
    def predict(self, samples):
        r = self.model.predict(samples)
        return r[1].ravel()


class PlateRecognition():
    def __init__(self):
        self.SZ = 20  # 训练图片长宽
        self.MAX_WIDTH = 1000  # 原始图片最大宽度
        self.Min_Area = 2000  # 车牌区域允许最大面积
        self.PROVINCE_START = 1000
        self.provinces = [
            "zh_cuan", "川",
            "zh_e", "鄂",
            "zh_gan", "赣",
            "zh_gan1", "甘",
            "zh_gui", "贵",
            "zh_gui1", "桂",
            "zh_hei", "黑",
            "zh_hu", "沪",
            "zh_ji", "冀",
            "zh_jin", "津",
            "zh_jing", "京",
            "zh_jl", "吉",
            "zh_liao", "辽",
            "zh_lu", "鲁",
            "zh_meng", "蒙",
            "zh_min", "闽",
            "zh_ning", "宁",
            "zh_qing", "靑",
            "zh_qiong", "琼",
            "zh_shan", "陕",
            "zh_su", "苏",
            "zh_sx", "晋",
            "zh_wan", "皖",
            "zh_xiang", "湘",
            "zh_xin", "新",
            "zh_yu", "豫",
            "zh_yu1", "渝",
            "zh_yue", "粤",
            "zh_yun", "云",
            "zh_zang", "藏",
            "zh_zhe", "浙"
        ]
        self.Prefecture = {
            '冀': {
                'A': ['河北省', '石家庄市'],
                'B': ['河北省', '唐山市'],
                'C': ['河北省', '秦皇岛市'],
                'D': ['河北省', '邯郸市'],
                'E': ['河北省', '邢台市'],
                'F': ['河北省', '保定市'],
                'G': ['河北省', '张家口市'],
                'H': ['河北省', '承德市'],
                'J': ['河北省', '沧州市'],
                'R': ['河北省', '廊坊市'],
                'S': ['河北省', '沧州市'],
                'T': ['河北省', '衡水市']
            },
            '辽': {
                'A': ['辽宁省', '沈阳市'],
                'B': ['辽宁省', '大连市'],
                'C': ['辽宁省', '鞍山市'],
                'D': ['辽宁省', '抚顺市'],
                'E': ['辽宁省', '本溪市'],
                'F': ['辽宁省', '丹东市'],
                'G': ['辽宁省', '锦州市'],
                'H': ['辽宁省', '营口市'],
                'J': ['辽宁省', '阜新市'],
                'K': ['辽宁省', '辽阳市'],
                'L': ['辽宁省', '盘锦市'],
                'M': ['辽宁省', '铁岭市'],
                'N': ['辽宁省', '朝阳市'],
                'P': ['辽宁省', '葫芦岛市']
            },
            '皖': {
                'A': ['安徽省', '合肥市'],
                'B': ['安徽省', '芜湖市'],
                'C': ['安徽省', '蚌埠市'],
                'D': ['安徽省', '淮南市'],
                'E': ['安徽省', '马鞍山市'],
                'F': ['安徽省', '淮北市'],
                'G': ['安徽省', '铜陵市'],
                'H': ['安徽省', '安庆市'],
                'J': ['安徽省', '黄山市'],
                'K': ['安徽省', '阜阳市'],
                'L': ['安徽省', '宿州市'],
                'M': ['安徽省', '滁州市'],
                'N': ['安徽省', '六安市'],
                'P': ['安徽省', '宣城市'],
                'Q': ['安徽省', '巢湖市'],
                'R': ['安徽省', '池州市'],
                'S': ['安徽省', '亳州市']
            },
            '苏': {
                'A': ['江苏省', '南京市'],
                'B': ['江苏省', '无锡市'],
                'C': ['江苏省', '徐州市'],
                'D': ['江苏省', '常州市'],
                'E': ['江苏省', '苏州市'],
                'F': ['江苏省', '南通市'],
                'G': ['江苏省', '连云港市'],
                'H': ['江苏省', '淮安市'],
                'J': ['江苏省', '盐城市'],
                'K': ['江苏省', '扬州市'],
                'L': ['江苏省', '镇江市'],
                'M': ['江苏省', '泰州市'],
                'N': ['江苏省', '宿迁市']
            },
            '鄂': {
                'A': ['湖北省', '武汉市'],
                'B': ['湖北省', '黄石市'],
                'C': ['湖北省', '十堰市'],
                'D': ['湖北省', '荆州市'],
                'E': ['湖北省', '宜昌市'],
                'F': ['湖北省', '襄樊市'],
                'G': ['湖北省', '鄂州市'],
                'H': ['湖北省', '荆门市'],
                'J': ['湖北省', '黄冈市'],
                'K': ['湖北省', '孝感市'],
                'L': ['湖北省', '咸宁市'],
                'M': ['湖北省', '仙桃市'],
                'N': ['湖北省', '潜江市'],
                'P': ['湖北省', '神农架林区'],
                'Q': ['湖北省', '恩施土家族苗族自治州'],
                'R': ['湖北省', '天门市'],
                'S': ['湖北省', '随州市']
            },
            '晋': {
                'A': ['山西省', '太原市'],
                'B': ['山西省', '大同市'],
                'C': ['山西省', '阳泉市'],
                'D': ['山西省', '长治市'],
                'E': ['山西省', '晋城市'],
                'F': ['山西省', '朔州市'],
                'H': ['山西省', '忻州市'],
                'J': ['山西省', '吕梁市'],
                'K': ['山西省', '晋中市'],
                'L': ['山西省', '临汾市'],
                'M': ['山西省', '运城市']
            },
            '吉': {
                'A': ['吉林省', '长春市'],
                'B': ['吉林省', '吉林市'],
                'C': ['吉林省', '四平市'],
                'D': ['吉林省', '辽源市'],
                'E': ['吉林省', '通化市'],
                'F': ['吉林省', '白山市'],
                'G': ['吉林省', '白城市'],
                'H': ['吉林省', '延边朝鲜族自治州'],
                'J': ['吉林省', '松原市'],
                'K': ['吉林省', '长白朝鲜族自治县']
            },
            '粤': {
                'A': ['广东省', '广州市'],
                'B': ['广东省', '深圳市'],
                'C': ['广东省', '珠海市'],
                'D': ['广东省', '汕头市'],
                'E': ['广东省', '佛山市'],
                'F': ['广东省', '韶关市'],
                'G': ['广东省', '湛江市'],
                'H': ['广东省', '肇庆市'],
                'J': ['广东省', '江门市'],
                'K': ['广东省', '茂名市'],
                'L': ['广东省', '惠州市'],
                'M': ['广东省', '梅州市'],
                'N': ['广东省', '汕尾市'],
                'P': ['广东省', '河源市'],
                'Q': ['广东省', '阳江市'],
                'R': ['广东省', '清远市'],
                'S': ['广东省', '东莞市'],
                'T': ['广东省', '中山市'],
                'U': ['广东省', '潮州市'],
                'V': ['广东省', '揭阳市'],
                'W': ['广东省', '云浮市'],
                'X': ['广东省', '顺德区'],
                'Y': ['广东省', '南海区'],
                'Z': ['广东省', '港澳进入内地车辆']
            },
            '藏': {
                'A': ['西藏自治区', '拉萨市'],
                'B': ['西藏自治区', '昌都地区'],
                'C': ['西藏自治区', '山南地区'],
                'D': ['西藏自治区', '日喀则地区'],
                'E': ['西藏自治区', '那曲地区'],
                'F': ['西藏自治区', '阿里地区'],
                'G': ['西藏自治区', '林芝地区'],
                'H': ['西藏自治区', '驻四川省天全县车辆管理所'],
                'J': ['西藏自治区', '驻青海省格尔木市车辆管理所']
            },
            '渝': {
                'A': ['重庆市'],
                'B': ['重庆市'],
                'C': ['重庆市'],
                'F': ['重庆市'],
                'G': ['重庆市'],
                'H': ['重庆市']
            },
            '沪': {
                'A': ['上海市'],
                'B': ['上海市'],
                'C': ['上海市'],
                'D': ['上海市'],
                'R': ['上海市']
            },
            '豫': {
                'A': ['河南省', '郑州市'],
                'B': ['河南省', '开封市'],
                'C': ['河南省', '洛阳市'],
                'D': ['河南省', '平顶山市'],
                'E': ['河南省', '安阳市'],
                'F': ['河南省', '鹤壁市'],
                'G': ['河南省', '新乡市'],
                'H': ['河南省', '焦作市'],
                'J': ['河南省', '濮阳市'],
                'K': ['河南省', '许昌市'],
                'L': ['河南省', '漯河市'],
                'M': ['河南省', '三门峡市'],
                'N': ['河南省', '商丘市'],
                'P': ['河南省', '周口市'],
                'Q': ['河南省', '驻马店市'],
                'R': ['河南省', '南阳市'],
                'S': ['河南省', '信阳市'],
                'U': ['河南省', '济源市']
            },
            '黑': {
                'A': ['黑龙江省', '哈尔滨市'],
                'B': ['黑龙江省', '齐齐哈尔市'],
                'C': ['黑龙江省', '牡丹江市'],
                'D': ['黑龙江省', '佳木斯市'],
                'E': ['黑龙江省', '大庆市'],
                'F': ['黑龙江省', '伊春市'],
                'G': ['黑龙江省', '鸡西市'],
                'H': ['黑龙江省', '鹤岗市'],
                'J': ['黑龙江省', '双鸭山市'],
                'K': ['黑龙江省', '七台河市'],
                'L': ['黑龙江省', '松花江地区（已并入哈尔滨市，车牌未改）'],
                'M': ['黑龙江省', '绥化市'],
                'N': ['黑龙江省', '黑河市'],
                'P': ['黑龙江省', '大兴安岭地区'],
                'R': ['黑龙江省', '农垦系统']
            },
            '鲁': {
                'A': ['山东省', '济南市'],
                'B': ['山东省', '青岛市'],
                'C': ['山东省', '淄博市'],
                'D': ['山东省', '枣庄市'],
                'E': ['山东省', '东营市'],
                'F': ['山东省', '烟台市'],
                'G': ['山东省', '潍坊市'],
                'H': ['山东省', '济宁市'],
                'J': ['山东省', '泰安市'],
                'K': ['山东省', '威海市'],
                'L': ['山东省', '日照市'],
                'M': ['山东省', '滨州市'],
                'N': ['山东省', '德州市'],
                'P': ['山东省', '聊城市'],
                'Q': ['山东省', '临沂市'],
                'R': ['山东省', '菏泽市'],
                'S': ['山东省', '莱芜市'],
                'U': ['山东省', '青岛市'],
                'V': ['山东省', '潍坊市'],
                'Y': ['山东省', '烟台市']
            },
            '浙': {
                'A': ['浙江省', '杭州市'],
                'B': ['浙江省', '宁波市'],
                'C': ['浙江省', '温州市'],
                'D': ['浙江省', '绍兴市'],
                'E': ['浙江省', '湖州市'],
                'F': ['浙江省', '嘉兴市'],
                'G': ['浙江省', '金华市'],
                'H': ['浙江省', '衢州市'],
                'J': ['浙江省', '台州市'],
                'K': ['浙江省', '丽水市'],
                'L': ['浙江省', '舟山市']
            },
            '桂': {
                'A': ['广西省', '南宁市'],
                'B': ['广西省', '柳州市'],
                'C': ['广西省', '桂林市'],
                'D': ['广西省', '梧州市'],
                'E': ['广西省', '北海市'],
                'F': ['广西省', '崇左市'],
                'G': ['广西省', '来宾市'],
                'H': ['广西省', '桂林市'],
                'J': ['广西省', '贺州市'],
                'K': ['广西省', '玉林市'],
                'M': ['广西省', '河池市'],
                'N': ['广西省', '钦州市'],
                'P': ['广西省', '防城港市'],
                'R': ['广西省', '贵港市']
            },
            '蒙': {
                'A': ['内蒙古自治区', '呼和浩特市'],
                'B': ['内蒙古自治区', '包头市'],
                'C': ['内蒙古自治区', '乌海市'],
                'D': ['内蒙古自治区', '赤峰市'],
                'E': ['内蒙古自治区', '呼伦贝尔市'],
                'F': ['内蒙古自治区', '兴安盟'],
                'G': ['内蒙古自治区', '通辽市'],
                'H': ['内蒙古自治区', '锡林郭勒盟'],
                'J': ['内蒙古自治区', '乌兰察布市'],
                'K': ['内蒙古自治区', '鄂尔多斯市'],
                'L': ['内蒙古自治区', '巴彦淖尔市'],
                'M': ['内蒙古自治区', '阿拉善盟']
            },
            '闽': {
                'A': ['福建省', '福州市'],
                'B': ['福建省', '莆田市'],
                'C': ['福建省', '泉州市'],
                'D': ['福建省', '厦门市'],
                'E': ['福建省', '漳州市'],
                'F': ['福建省', '龙岩市'],
                'G': ['福建省', '三明市'],
                'H': ['福建省', '南平市'],
                'J': ['福建省', '宁德市'],
                'K': ['福建省', '省直系统']
            },
            '川': {
                'A': ['四川省', '成都市'],
                'B': ['四川省', '绵阳市'],
                'C': ['四川省', '自贡市'],
                'D': ['四川省', '攀枝花市'],
                'E': ['四川省', '泸州市'],
                'F': ['四川省', '德阳市'],
                'H': ['四川省', '广元市'],
                'J': ['四川省', '遂宁市'],
                'K': ['四川省', '内江市'],
                'L': ['四川省', '乐山市'],
                'M': ['四川省', '资阳市'],
                'Q': ['四川省', '宜宾市'],
                'R': ['四川省', '南充市'],
                'S': ['四川省', '达州市'],
                'T': ['四川省', '雅安市'],
                'U': ['四川省', '阿坝藏族羌族自治州'],
                'V': ['四川省', '甘孜藏族自治州'],
                'W': ['四川省', '凉山彝族自治州'],
                'X': ['四川省', '广安市'],
                'Y': ['四川省', '巴中市'],
                'Z': ['四川省', '眉山市']
            },
            '琼': {
                'A': ['海南省', '海口市'],
                'B': ['海南省', '三亚市'],
                'C': ['海南省', '琼海市'],
                'D': ['海南省', '五指山市'],
                'E': ['海南省', '洋浦开发区']
            },
            '京': {
                'A': ['北京市'],
                'B': ['北京市'],
                'C': ['北京市'],
                'D': ['北京市'],
                'E': ['北京市'],
                'F': ['北京市'],
                'G': ['北京市'],
                'H': ['北京市'],
                'J': ['北京市'],
                'K': ['北京市'],
                'L': ['北京市'],
                'M': ['北京市'],
                'N': ['北京市'],
                'P': ['北京市'],
                'Q': ['北京市']
            },
            '云': {
                'A': ['云南省', '昆明市'],
                'C': ['云南省', '昭通市'],
                'D': ['云南省', '曲靖市'],
                'E': ['云南省', '楚雄彝族自治州'],
                'F': ['云南省', '玉溪市'],
                'G': ['云南省', '红河哈尼族彝族自治州'],
                'H': ['云南省', '文山壮族苗族自治州'],
                'J': ['云南省', '思茅区'],
                'K': ['云南省', '西双版纳傣族自治州'],
                'L': ['云南省', '大理白族自治州'],
                'M': ['云南省', '保山市'],
                'N': ['云南省', '德宏傣族景颇族自治州'],
                'P': ['云南省', '丽江市'],
                'Q': ['云南省', '怒江傈僳族自治州'],
                'R': ['云南省', '迪庆藏族自治州'],
                'S': ['云南省', '临沧市']
            },
            '湘': {
                'A': ['湖南省', '长沙市'],
                'B': ['湖南省', '株洲市'],
                'C': ['湖南省', '湘潭市'],
                'D': ['湖南省', '衡阳市'],
                'E': ['湖南省', '邵阳市'],
                'F': ['湖南省', '岳阳市'],
                'G': ['湖南省', '张家界市'],
                'H': ['湖南省', '益阳市'],
                'J': ['湖南省', '常德市'],
                'K': ['湖南省', '娄底市'],
                'L': ['湖南省', '郴州市'],
                'M': ['湖南省', '永州市'],
                'N': ['湖南省', '怀化市'],
                'U': ['湖南省', '湘西土家族苗族自治州']
            },
            '新': {
                'A': ['新疆维吾尔自治区', '乌鲁木齐市'],
                'B': ['新疆维吾尔自治区', '昌吉回族自治州'],
                'C': ['新疆维吾尔自治区', '石河子市'],
                'D': ['新疆维吾尔自治区', '奎屯市'],
                'E': ['新疆维吾尔自治区', '博尔塔拉蒙古自治州'],
                'F': ['新疆维吾尔自治区', '伊犁哈萨克自治州'],
                'G': ['新疆维吾尔自治区', '塔城地区'],
                'H': ['新疆维吾尔自治区', '阿勒泰地区'],
                'J': ['新疆维吾尔自治区', '克拉玛依市'],
                'K': ['新疆维吾尔自治区', '吐鲁番地区'],
                'L': ['新疆维吾尔自治区', '哈密地区'],
                'M': ['新疆维吾尔自治区', '巴音郭愣蒙古自治州'],
                'N': ['新疆维吾尔自治区', '阿克苏地区'],
                'P': ['新疆维吾尔自治区', '克孜勒苏柯尔克孜自治州'],
                'Q': ['新疆维吾尔自治区', '喀什地区'],
                'R': ['新疆维吾尔自治区', '和田地区']
            },
            '赣': {
                'A': ['江西省', '南昌市'],
                'B': ['江西省', '赣州市'],
                'C': ['江西省', '宜春市'],
                'D': ['江西省', '吉安市'],
                'E': ['江西省', '上饶市'],
                'F': ['江西省', '抚州市'],
                'G': ['江西省', '九江市'],
                'H': ['江西省', '景德镇市'],
                'J': ['江西省', '萍乡市'],
                'K': ['江西省', '新余市'],
                'L': ['江西省', '鹰潭市'],
                'M': ['江西省', '南昌市']
            },
            '甘': {
                'A': ['甘肃省', '兰州市'],
                'B': ['甘肃省', '嘉峪关市'],
                'C': ['甘肃省', '金昌市'],
                'D': ['甘肃省', '白银市'],
                'E': ['甘肃省', '天水市'],
                'F': ['甘肃省', '酒泉市'],
                'G': ['甘肃省', '张掖市'],
                'H': ['甘肃省', '武威市'],
                'J': ['甘肃省', '定西市'],
                'K': ['甘肃省', '陇南市'],
                'L': ['甘肃省', '平凉市'],
                'M': ['甘肃省', '庆阳市'],
                'N': ['甘肃省', '临夏回族自治州'],
                'P': ['甘肃省', '甘南藏族自治州']
            },
            '陕': {
                'A': ['陕西省', '西安市'],
                'B': ['陕西省', '铜川市'],
                'C': ['陕西省', '宝鸡市'],
                'D': ['陕西省', '咸阳市'],
                'E': ['陕西省', '渭南市'],
                'F': ['陕西省', '汉中市'],
                'G': ['陕西省', '安康市'],
                'H': ['陕西省', '商洛市'],
                'J': ['陕西省', '延安市'],
                'K': ['陕西省', '榆林市'],
                'V': ['陕西省', '杨凌区']
            },
            '贵': {
                'A': ['贵族省', '贵阳市'],
                'B': ['贵族省', '六盘水市'],
                'C': ['贵族省', '遵义市'],
                'D': ['贵族省', '铜仁地区'],
                'E': ['贵族省', '黔西南布依族苗族自治州'],
                'F': ['贵族省', '毕节地区'],
                'G': ['贵族省', '安顺市'],
                'H': ['贵族省', '黔东南苗族侗族自治州'],
                'J': ['贵族省', '黔南布依族苗族自治州']
            },
            '青': {
                'A': ['青海省', '西宁市'],
                'B': ['青海省', '海东地区'],
                'C': ['青海省', '海北藏族自治州'],
                'D': ['青海省', '黄南藏族自治州'],
                'E': ['青海省', '海南藏族自治州'],
                'F': ['青海省', '果洛藏族自治州'],
                'G': ['青海省', '玉树藏族自治州'],
                'H': ['青海省', '海西蒙古族藏族自治州']
            },
            '宁': {
                'A': ['宁夏回族自治区', '银川市'],
                'B': ['宁夏回族自治区', '石嘴山市'],
                'C': ['宁夏回族自治区', '银南市'],
                'D': ['宁夏回族自治区', '固原市'],
                'E': ['宁夏回族自治区', '中卫市']
            },
            '津': {
                'A': ['天津市'],
                'B': ['天津市'],
                'C': ['天津市'],
                'D': ['天津市'],
                'E': ['天津市'],
                'F': ['天津市'],
                'G': ['天津市'],
                'H': ['天津市']
            }
        }  # 字母所代表的地区
        self.cardtype = {
            'blue': '蓝色牌照',
            'green': '绿色牌照',
            'yellow': '黄色牌照'
        }  # 不同颜色含义
        # 车牌识别的部分参数保存在js中，便于根据图片分辨率做调整
        f = open('config.js')
        j = json.load(f)
        for c in j["config"]:
            if c["open"]:
                self.cfg = c.copy()
                break
        else:
            raise RuntimeError('没有设置有效配置参数')

    def __del__(self):
        self.save_traindata()

    # 读取图片文件
    def __imreadex(self, filename):
        return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), cv2.IMREAD_COLOR)

    def __point_limit(self, point):
        if point[0] < 0:
            point[0] = 0
        if point[1] < 0:
            point[1] = 0

    # 利用投影法，根据设定的阈值和图片直方图，找出波峰，用于分隔字符
    def __find_waves(self, threshold, histogram):
        up_point = -1  # 上升点
        is_peak = False
        if histogram[0] > threshold:
            up_point = 0
            is_peak = True
        wave_peaks = []
        for i, x in enumerate(histogram):
            if is_peak and x < threshold:
                if i - up_point > 2:
                    is_peak = False
                    wave_peaks.append((up_point, i))
            elif not is_peak and x >= threshold:
                is_peak = True
                up_point = i
        if is_peak and up_point != -1 and i - up_point > 4:
            wave_peaks.append((up_point, i))
        return wave_peaks

    # 根据找出的波峰，分隔图片，从而得到逐个字符图片
    def __seperate_card(self, img, waves):
        part_cards = []
        for wave in waves:
            part_cards.append(img[:, wave[0]:wave[1]])
        return part_cards

    # 来自opencv的sample，用于svm训练
    def __deskew(self, img):
        m = cv2.moments(img)
        if abs(m['mu02']) < 1e-2:
            return img.copy()
        skew = m['mu11'] / m['mu02']
        M = np.float32([[1, skew, -0.5 * self.SZ * skew], [0, 1, 0]])
        img = cv2.warpAffine(img, M, (self.SZ, self.SZ), flags=cv2.WARP_INVERSE_MAP | cv2.INTER_LINEAR)
        return img

    # 来自opencv的sample，用于svm训练
    def __preprocess_hog(self, digits):
        samples = []
        for img in digits:
            gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
            gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
            mag, ang = cv2.cartToPolar(gx, gy)
            bin_n = 16
            bin = np.int32(bin_n * ang / (2 * np.pi))
            bin_cells = bin[:10, :10], bin[10:, :10], bin[:10, 10:], bin[10:, 10:]
            mag_cells = mag[:10, :10], mag[10:, :10], mag[:10, 10:], mag[10:, 10:]
            hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
            hist = np.hstack(hists)

            # transform to Hellinger kernel
            eps = 1e-7
            hist /= hist.sum() + eps
            hist = np.sqrt(hist)
            hist /= norm(hist) + eps

            samples.append(hist)
        return np.float32(samples)

    def train_svm(self):
        # 识别英文字母和数字
        self.model = SVM(C=1, gamma=0.5)
        # 识别中文
        self.modelchinese = SVM(C=1, gamma=0.5)
        if os.path.exists("svm.dat"):
            self.model.load("svm.dat")
        else:
            chars_train = []
            chars_label = []

            for root, dirs, files in os.walk("train\\chars2"):
                if len(os.path.basename(root)) > 1:
                    continue
                root_int = ord(os.path.basename(root))
                for filename in files:
                    filepath = os.path.join(root, filename)
                    digit_img = cv2.imread(filepath)
                    digit_img = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)
                    chars_train.append(digit_img)
                    # chars_label.append(1)
                    chars_label.append(root_int)

            chars_train = list(map(self.__deskew, chars_train))
            chars_train = self.__preprocess_hog(chars_train)
            # chars_train = chars_train.reshape(-1, 20, 20).astype(np.float32)
            chars_label = np.array(chars_label)
            # print(chars_train.shape)
            self.model.train(chars_train, chars_label)
        if os.path.exists("svmchinese.dat"):
            self.modelchinese.load("svmchinese.dat")
        else:
            chars_train = []
            chars_label = []
            for root, dirs, files in os.walk("train\\charsChinese"):
                if not os.path.basename(root).startswith("zh_"):
                    continue
                pinyin = os.path.basename(root)
                index = self.provinces.index(pinyin) + self.PROVINCE_START + 1  # 1是拼音对应的汉字
                for filename in files:
                    filepath = os.path.join(root, filename)
                    digit_img = cv2.imread(filepath)
                    digit_img = cv2.cvtColor(digit_img, cv2.COLOR_BGR2GRAY)
                    chars_train.append(digit_img)
                    # chars_label.append(1)
                    chars_label.append(index)
            chars_train = list(map(self.__deskew, chars_train))
            chars_train = self.__preprocess_hog(chars_train)
            # chars_train = chars_train.reshape(-1, 20, 20).astype(np.float32)
            chars_label = np.array(chars_label)
            # print(chars_train.shape)
            self.modelchinese.train(chars_train, chars_label)

    def save_traindata(self):
        if not os.path.exists("svm.dat"):
            self.model.save("svm.dat")
        if not os.path.exists("svmchinese.dat"):
            self.modelchinese.save("svmchinese.dat")

    def accurate_place(self, card_img_hsv, limit1, limit2, color):
        row_num, col_num = card_img_hsv.shape[:2]
        xl = col_num
        xr = 0
        yh = 0
        yl = row_num
        # col_num_limit = self.cfg["col_num_limit"]
        row_num_limit = self.cfg["row_num_limit"]
        col_num_limit = col_num * 0.8 if color != "green" else col_num * 0.5  # 绿色有渐变
        for i in range(row_num):
            count = 0
            for j in range(col_num):
                H = card_img_hsv.item(i, j, 0)
                S = card_img_hsv.item(i, j, 1)
                V = card_img_hsv.item(i, j, 2)
                if limit1 < H <= limit2 and 34 < S and 46 < V:
                    count += 1
            if count > col_num_limit:
                if yl > i:
                    yl = i
                if yh < i:
                    yh = i
        for j in range(col_num):
            count = 0
            for i in range(row_num):
                H = card_img_hsv.item(i, j, 0)
                S = card_img_hsv.item(i, j, 1)
                V = card_img_hsv.item(i, j, 2)
                if limit1 < H <= limit2 and 34 < S and 46 < V:
                    count += 1
            if count > row_num - row_num_limit:
                if xl > j:
                    xl = j
                if xr < j:
                    xr = j
        return xl, xr, yh, yl

    # 预处理
    def __preTreatment(self, car_pic):
        if type(car_pic) == type(""):
            img = self.__imreadex(car_pic)
        else:
            img = car_pic
        pic_hight, pic_width = img.shape[:2]

        if pic_width > self.MAX_WIDTH:
            resize_rate = self.MAX_WIDTH / pic_width
            img = cv2.resize(img, (self.MAX_WIDTH, int(pic_hight * resize_rate)),
                             interpolation=cv2.INTER_AREA)  # 图片分辨率调整
        # cv2.imshow('Image', img)

        blur = self.cfg["blur"]
        # 高斯去噪
        if blur > 0:
            img = cv2.GaussianBlur(img, (blur, blur), 0)
        oldimg = img
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('GaussianBlur', img)

        # 去掉图像中不会是车牌的区域
        kernel = np.ones((20, 20), np.uint8)
        img_opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)  # 开运算
        img_opening = cv2.addWeighted(img, 1, img_opening, -1, 0);  # 与上一次开运算结果融合
        # cv2.imshow('img_opening', img_opening)

        # 找到图像边缘
        ret, img_thresh = cv2.threshold(img_opening, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # 二值化
        img_edge = cv2.Canny(img_thresh, 100, 200)
        # cv2.imshow('img_edge', img_edge)

        # 使用开运算和闭运算让图像边缘成为一个整体
        kernel = np.ones((self.cfg["morphologyr"], self.cfg["morphologyc"]), np.uint8)
        img_edge1 = cv2.morphologyEx(img_edge, cv2.MORPH_CLOSE, kernel)  # 闭运算
        img_edge2 = cv2.morphologyEx(img_edge1, cv2.MORPH_OPEN, kernel)  # 开运算
        # cv2.imshow('img_edge2', img_edge2)

        # 查找图像边缘整体形成的矩形区域，可能有很多，车牌就在其中一个矩形区域中
        image, contours, hierarchy = cv2.findContours(img_edge2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = [cnt for cnt in contours if cv2.contourArea(cnt) > self.Min_Area]
        # print(contours[0])

        # 逐个排除不是车牌的矩形区域
        car_contours = []
        for cnt in contours:
            # 框选 生成最小外接矩形 返回值（中心(x,y), (宽,高), 旋转角度）
            rect = cv2.minAreaRect(cnt)
            # print('宽高:',rect[1])
            area_width, area_height = rect[1]
            # 选择宽大于高的区域
            if area_width < area_height:
                area_width, area_height = area_height, area_width
            wh_ratio = area_width / area_height
            # print('宽高比：',wh_ratio)
            # 要求矩形区域长宽比在2到5.5之间，2到5.5是车牌的长宽比，其余的矩形排除
            if wh_ratio > 2 and wh_ratio < 5.5:
                car_contours.append(rect)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
            # oldimg = cv2.drawContours(oldimg, [box], 0, (0, 0, 255), 2)
            # cv2.imshow("Test",oldimg )
            # print(car_contours)

        # 矩形区域可能是倾斜的矩形，需要矫正，以便使用颜色定位
        card_imgs = []
        for rect in car_contours:
            if rect[2] > -1 and rect[2] < 1:  # 创造角度，使得左、高、右、低拿到正确的值
                angle = 1
            else:
                angle = rect[2]
            rect = (rect[0], (rect[1][0] + 5, rect[1][1] + 5), angle)  # 扩大范围，避免车牌边缘被排除
            box = cv2.boxPoints(rect)
            heigth_point = right_point = [0, 0]
            left_point = low_point = [pic_width, pic_hight]
            for point in box:
                if left_point[0] > point[0]:
                    left_point = point
                if low_point[1] > point[1]:
                    low_point = point
                if heigth_point[1] < point[1]:
                    heigth_point = point
                if right_point[0] < point[0]:
                    right_point = point

            if left_point[1] <= right_point[1]:  # 正角度
                new_right_point = [right_point[0], heigth_point[1]]
                pts2 = np.float32([left_point, heigth_point, new_right_point])  # 字符只是高度需要改变
                pts1 = np.float32([left_point, heigth_point, right_point])
                M = cv2.getAffineTransform(pts1, pts2)
                dst = cv2.warpAffine(oldimg, M, (pic_width, pic_hight))
                self.__point_limit(new_right_point)
                self.__point_limit(heigth_point)
                self.__point_limit(left_point)
                card_img = dst[int(left_point[1]):int(heigth_point[1]), int(left_point[0]):int(new_right_point[0])]
                card_imgs.append(card_img)

            elif left_point[1] > right_point[1]:  # 负角度

                new_left_point = [left_point[0], heigth_point[1]]
                pts2 = np.float32([new_left_point, heigth_point, right_point])  # 字符只是高度需要改变
                pts1 = np.float32([left_point, heigth_point, right_point])
                M = cv2.getAffineTransform(pts1, pts2)
                dst = cv2.warpAffine(oldimg, M, (pic_width, pic_hight))
                self.__point_limit(right_point)
                self.__point_limit(heigth_point)
                self.__point_limit(new_left_point)
                card_img = dst[int(right_point[1]):int(heigth_point[1]), int(new_left_point[0]):int(right_point[0])]
                card_imgs.append(card_img)
        # cv2.imshow("card", card_imgs[0])

        # #____开始使用颜色定位，排除不是车牌的矩形，目前只识别蓝、绿、黄车牌
        colors = []
        for card_index, card_img in enumerate(card_imgs):
            green = yellow = blue = black = white = 0
            try:
                # 有转换失败的可能，原因来自于上面矫正矩形出错
                card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
            except:
                print('BGR转HSV失败')
                card_imgs = colors = None
                return card_imgs, colors

            if card_img_hsv is None:
                continue
            row_num, col_num = card_img_hsv.shape[:2]
            card_img_count = row_num * col_num

            # 确定车牌颜色
            for i in range(row_num):
                for j in range(col_num):
                    H = card_img_hsv.item(i, j, 0)
                    S = card_img_hsv.item(i, j, 1)
                    V = card_img_hsv.item(i, j, 2)
                    if 11 < H <= 34 and S > 34:  # 图片分辨率调整
                        yellow += 1
                    elif 35 < H <= 99 and S > 34:  # 图片分辨率调整
                        green += 1
                    elif 99 < H <= 124 and S > 34:  # 图片分辨率调整
                        blue += 1

                    if 0 < H < 180 and 0 < S < 255 and 0 < V < 46:
                        black += 1
                    elif 0 < H < 180 and 0 < S < 43 and 221 < V < 225:
                        white += 1
            color = "no"
            # print('黄：{:<6}绿：{:<6}蓝：{:<6}'.format(yellow,green,blue))

            limit1 = limit2 = 0
            if yellow * 2 >= card_img_count:
                color = "yellow"
                limit1 = 11
                limit2 = 34  # 有的图片有色偏偏绿
            elif green * 2 >= card_img_count:
                color = "green"
                limit1 = 35
                limit2 = 99
            elif blue * 2 >= card_img_count:
                color = "blue"
                limit1 = 100
                limit2 = 124  # 有的图片有色偏偏紫
            elif black + white >= card_img_count * 0.7:
                color = "bw"
            # print(color)
            colors.append(color)
            # print(blue, green, yellow, black, white, card_img_count)
            if limit1 == 0:
                continue

            # 根据车牌颜色再定位，缩小边缘非车牌边界
            xl, xr, yh, yl = self.accurate_place(card_img_hsv, limit1, limit2, color)
            if yl == yh and xl == xr:
                continue
            need_accurate = False
            if yl >= yh:
                yl = 0
                yh = row_num
                need_accurate = True
            if xl >= xr:
                xl = 0
                xr = col_num
                need_accurate = True
            card_imgs[card_index] = card_img[yl:yh, xl:xr] \
                if color != "green" or yl < (yh - yl) // 4 else card_img[yl - (yh - yl) // 4:yh, xl:xr]
            if need_accurate:  # 可能x或y方向未缩小，需要再试一次
                card_img = card_imgs[card_index]
                card_img_hsv = cv2.cvtColor(card_img, cv2.COLOR_BGR2HSV)
                xl, xr, yh, yl = self.accurate_place(card_img_hsv, limit1, limit2, color)
                if yl == yh and xl == xr:
                    continue
                if yl >= yh:
                    yl = 0
                    yh = row_num
                if xl >= xr:
                    xl = 0
                    xr = col_num
            card_imgs[card_index] = card_img[yl:yh, xl:xr] \
                if color != "green" or yl < (yh - yl) // 4 else card_img[yl - (yh - yl) // 4:yh, xl:xr]
        # cv2.imshow("result", card_imgs[0])
        # cv2.imwrite('1.jpg', card_imgs[0])
        # print('颜色识别结果：' + colors[0])
        return card_imgs, colors

    # 分割字符并识别车牌文字
    def __identification(self, card_imgs, colors):
        # 识别车牌中的字符
        result = {}
        predict_result = []
        roi = None
        card_color = None
        for i, color in enumerate(colors):
            if color in ("blue", "yellow", "green"):
                card_img = card_imgs[i]
                # RGB转GARY
                gray_img = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
                # cv2.imshow('gray_img', gray_img)

                # 黄、绿车牌字符比背景暗、与蓝车牌刚好相反，所以黄、绿车牌需要反向
                if color == "green" or color == "yellow":
                    gray_img = cv2.bitwise_not(gray_img)
                # 二值化
                ret, gray_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                # cv2.imshow('gray_img', gray_img)

                # 查找水平直方图波峰
                x_histogram = np.sum(gray_img, axis=1)
                # 最小值
                x_min = np.min(x_histogram)
                # 均值
                x_average = np.sum(x_histogram) / x_histogram.shape[0]
                x_threshold = (x_min + x_average) / 2
                wave_peaks = self.__find_waves(x_threshold, x_histogram)
                if len(wave_peaks) == 0:
                    continue

                # 认为水平方向，最大的波峰为车牌区域
                wave = max(wave_peaks, key=lambda x: x[1] - x[0])
                gray_img = gray_img[wave[0]:wave[1]]
                # cv2.imshow('gray_img', gray_img)

                # 查找垂直直方图波峰
                row_num, col_num = gray_img.shape[:2]
                # 去掉车牌上下边缘1个像素，避免白边影响阈值判断
                gray_img = gray_img[1:row_num - 1]
                # cv2.imshow('gray_img', gray_img)
                y_histogram = np.sum(gray_img, axis=0)
                y_min = np.min(y_histogram)
                y_average = np.sum(y_histogram) / y_histogram.shape[0]
                y_threshold = (y_min + y_average) / 5  # U和0要求阈值偏小，否则U和0会被分成两半

                wave_peaks = self.__find_waves(y_threshold, y_histogram)
                # print(wave_peaks)

                # for wave in wave_peaks:
                #	cv2.line(card_img, pt1=(wave[0], 5), pt2=(wave[1], 5), color=(0, 0, 255), thickness=2)
                # 车牌字符数应大于6
                if len(wave_peaks) <= 6:
                    #   print(wave_peaks)
                    continue

                wave = max(wave_peaks, key=lambda x: x[1] - x[0])
                max_wave_dis = wave[1] - wave[0]
                # 判断是否是左侧车牌边缘
                if wave_peaks[0][1] - wave_peaks[0][0] < max_wave_dis / 3 and wave_peaks[0][0] == 0:
                    wave_peaks.pop(0)

                # 组合分离汉字
                cur_dis = 0
                for i, wave in enumerate(wave_peaks):
                    if wave[1] - wave[0] + cur_dis > max_wave_dis * 0.6:
                        break
                    else:
                        cur_dis += wave[1] - wave[0]
                if i > 0:
                    wave = (wave_peaks[0][0], wave_peaks[i][1])
                    wave_peaks = wave_peaks[i + 1:]
                    wave_peaks.insert(0, wave)

                # 去除车牌上的分隔点
                point = wave_peaks[2]
                if point[1] - point[0] < max_wave_dis / 3:
                    point_img = gray_img[:, point[0]:point[1]]
                    if np.mean(point_img) < 255 / 5:
                        wave_peaks.pop(2)

                if len(wave_peaks) <= 6:
                    # print("peak less 2:", wave_peaks)
                    continue
                # print(wave_peaks)
                # 分割牌照字符
                part_cards = self.__seperate_card(gray_img, wave_peaks)
                # for i, part_card in enumerate(part_cards):
                #    cv2.imshow(str(i), part_card)

                # 识别
                for i, part_card in enumerate(part_cards):
                    # 可能是固定车牌的铆钉
                    if np.mean(part_card) < 255 / 5:
                        continue
                    part_card_old = part_card
                    w = abs(part_card.shape[1] - self.SZ) // 2

                    # 边缘填充
                    part_card = cv2.copyMakeBorder(part_card, 0, 0, w, w, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                    # cv2.imshow('part_card', part_card)

                    # 图片缩放（缩小）
                    part_card = cv2.resize(part_card, (self.SZ, self.SZ), interpolation=cv2.INTER_AREA)
                    # cv2.imshow('part_card', part_card)

                    part_card = self.__preprocess_hog([part_card])
                    if i == 0:  # 识别汉字
                        resp = self.modelchinese.predict(part_card)  # 匹配样本
                        charactor = self.provinces[int(resp[0]) - self.PROVINCE_START]
                        # print(charactor)
                    else:  # 识别字母
                        resp = self.model.predict(part_card)  # 匹配样本
                        charactor = chr(resp[0])
                        # print(charactor)
                    # 判断最后一个数是否是车牌边缘，假设车牌边缘被认为是1
                    if charactor == "1" and i == len(part_cards) - 1:
                        if color == 'blue' and len(part_cards) > 7:
                            if part_card_old.shape[0] / part_card_old.shape[1] >= 7:  # 1太细，认为是边缘
                                continue
                        elif color == 'blue' and len(part_cards) > 7:
                            if part_card_old.shape[0] / part_card_old.shape[1] >= 7:  # 1太细，认为是边缘
                                continue
                        elif color == 'green' and len(part_cards) > 8:
                            if part_card_old.shape[0] / part_card_old.shape[1] >= 7:  # 1太细，认为是边缘
                                continue
                    predict_result.append(charactor)
                roi = card_img
                card_color = color
                break

        return predict_result, roi, card_color  # 识别到的字符、定位的车牌图像、车牌颜色

    def vehicleLicensePlateRecognition(self, car_pic):
        result = {}
        start = time.time()
        self.train_svm()
        card_imgs, colors = self.__preTreatment(car_pic)
        if card_imgs is None:
            return
        else:
            predict_result, roi, card_color = self.__identification(card_imgs, colors)
            if predict_result != []:
                result['UseTime'] = round((time.time() - start), 2)
                result['InputTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
                result['Type'] = self.cardtype[card_color]
                result['List'] = predict_result
                result['Number'] = ''.join(predict_result[:2]) + '·' + ''.join(predict_result[2:])
                result['Picture'] = roi
                try:
                    result['From'] = ''.join(self.Prefecture[result['List'][0]][result['List'][1]])
                except:
                    result['From'] = '未知'
                return result
            else:
                return None

    def VLPR(self, car_pic):
        result = {}
        start = time.time()
        self.train_svm()
        card_imgs, colors = self.__preTreatment(car_pic)
        if card_imgs is None:
            return
        else:
            predict_result, roi, card_color = self.__identification(card_imgs, colors)
            if predict_result != []:
                result['UseTime'] = round((time.time() - start), 2)
                result['InputTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
                result['Type'] = self.cardtype[card_color]
                result['List'] = predict_result
                result['Number'] = ''.join(predict_result[:2]) + '·' + ''.join(predict_result[2:])
                result['Picture'] = roi
                try:
                    result['From'] = ''.join(self.Prefecture[result['List'][0]][result['List'][1]])
                except:
                    result['From'] = '未知'
                return result
            else:
                return None


if __name__ == '__main__':
    c = PlateRecognition()
    result = c.VLPR("./test/蒙AGX468.jpg")
    print(result)
    # print(result['List'])
    # print(result['Type'])
    cv2.waitKey(0)
