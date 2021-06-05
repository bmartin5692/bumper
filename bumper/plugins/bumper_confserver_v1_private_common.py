#!/usr/bin/env python3
import logging

from aiohttp import web

from bumper import plugins
from bumper.models import *


class v1_private_common(plugins.ConfServerApp):

    def __init__(self):
        self.name = "v1_private_common"
        self.plugin_type = "sub_api"
        self.sub_api = "api_v1"

        self.routes = [
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkAPPVersion", self.handle_checkAPPVersion, name="v1_common_checkAppVersion"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/checkVersion", self.handle_checkVersion, name="v1_common_checkVersion"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/uploadDeviceInfo", self.handle_uploadDeviceInfo, name="v1_common_uploadDeviceInfo"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getSystemReminder", self.handle_getSystemReminder, name="v1_common_getSystemReminder"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getConfig",self.handle_getConfig, name="v1_common_getConfig"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getAreas",self.handle_getAreas, name="v1_common_getAreas"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getAgreementURLBatch", self.handle_getAgreementURLBatch, name="v1_common_getAgreementURLBatch"),
            web.route("*", "/private/{country}/{language}/{devid}/{apptype}/{appversion}/{devtype}/{aid}/common/getTimestamp", self.handle_getTimestamp, name="v1_common_getTimestamp"),

        ]

        self.get_milli_time = bumper.ConfServer.ConfServer_GeneralFunctions().get_milli_time

    async def handle_checkVersion(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "img": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_checkAPPVersion(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "c": None,
                    "downPageUrl": None,
                    "img": None,
                    "nextAlertTime": None,
                    "r": 0,
                    "t": None,
                    "u": None,
                    "ut": 0,
                    "v": None,
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_uploadDeviceInfo(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": None,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getSystemReminder(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "iosGradeTime": {"iodGradeFlag": "N"},
                    "openNotification": {
                        "openNotificationContent": None,
                        "openNotificationFlag": "N",
                        "openNotificationTitle": None,
                    },
                },
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getConfig(self, request):
        try:
            data = []
            for key in request.query["keys"].split(','):
                data.append({
                    "key": key,
                    "value": "Y"
                })

            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": data,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getAreas(self, request):
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": AREA_LIST,
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getAgreementURLBatch(self, request):  # EcoVacs Home
        try:
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": [
                    {
                        "acceptTime": None,
                        "force": None,
                        "id": "20180804040641_7d746faf18b8cb22a50d145598fe4c90",
                        "type": "USER",
                        "url": "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040641_7d746faf18b8cb22a50d145598fe4c90&language=EN",
                        "version": "1.03"
                    },
                    {
                        "acceptTime": None,
                        "force": None,
                        "id": "20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac",
                        "type": "PRIVACY",
                        "url": "https://gl-eu-wap.ecovacs.com/content/agreement?id=20180804040245_4e7c56dfb7ebd3b81b1f2747d0859fac&language=EN",
                        "version": "1.03"
                    }
                ],
                "msg": "操作成功",
                "success": True,
                "time": self.get_milli_time(datetime.utcnow().timestamp()),
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))

    async def handle_getTimestamp(self, request):  # EcoVacs Home
        try:
            time = self.get_milli_time(datetime.utcnow().timestamp())
            body = {
                "code": bumper.RETURN_API_SUCCESS,
                "data": {
                    "timestamp": time
                },
                "msg": "操作成功",
                "success": True,
                "time": time,
            }

            return web.json_response(body)

        except Exception as e:
            logging.exception("{}".format(e))


plugin = v1_private_common()

AREA_LIST = {"currentVersion": 231,
             "areaList": [{"areaKey": "JP", "chsName": "日本", "enName": "Japan", "pyFirst": "R"},
                          {"areaKey": "MY", "chsName": "马来西亚", "enName": "Malaysia", "pyFirst": "M"},
                          {"areaKey": "DE", "chsName": "德国", "enName": "Germany", "pyFirst": "D"},
                          {"areaKey": "LI", "chsName": "列支敦斯登", "enName": "Liechtenstein", "pyFirst": "L"},
                          {"areaKey": "AT", "chsName": "奥地利", "enName": "Austria", "pyFirst": "A"},
                          {"areaKey": "TW", "chsName": "台湾", "enName": "Taiwan", "pyFirst": "T"},
                          {"areaKey": "FR", "chsName": "法国", "enName": "France", "pyFirst": "F"},
                          {"areaKey": "CN", "chsName": "中国大陆", "enName": "China Mainland", "pyFirst": "Z"},
                          {"areaKey": "SG", "chsName": "新加坡", "enName": "Singapore", "pyFirst": "X"},
                          {"areaKey": "RE", "chsName": "留尼汪岛", "enName": "Reunion Island", "pyFirst": "L"},
                          {"areaKey": "EH", "chsName": "西撒哈拉", "enName": "Western Sahara", "pyFirst": "X"},
                          {"areaKey": "WF", "chsName": "瓦利斯群岛和富图纳群岛", "enName": "Wallis and Futuna Islands",
                           "pyFirst": "W"},
                          {"areaKey": "KP", "chsName": "朝鲜", "enName": "North Korea", "pyFirst": "C"},
                          {"areaKey": "ZW", "chsName": "津巴布韦", "enName": "Zimbabwe", "pyFirst": "J"},
                          {"areaKey": "VI", "chsName": "美属维尔京群岛", "enName": "United States Virgin Islands",
                           "pyFirst": "M"},
                          {"areaKey": "PF", "chsName": "法属玻里尼西亚", "enName": "French Polynesia",
                           "pyFirst": "F"},
                          {"areaKey": "DJ", "chsName": "吉布提", "enName": "Djibouti", "pyFirst": "J"},
                          {"areaKey": "KZ", "chsName": "哈萨克斯坦", "enName": "Kazakhstan", "pyFirst": "H"},
                          {"areaKey": "TV", "chsName": "图瓦卢", "enName": "Tuvalu", "pyFirst": "T"},
                          {"areaKey": "VU", "chsName": "瓦努阿图", "enName": "Vanuatu", "pyFirst": "W"},
                          {"areaKey": "IN", "chsName": "印度", "enName": "India", "pyFirst": "Y"},
                          {"areaKey": "CM", "chsName": "喀麦隆", "enName": "Cameroon", "pyFirst": "K"},
                          {"areaKey": "LK", "chsName": "斯里兰卡", "enName": "Sri Lanka", "pyFirst": "S"},
                          {"areaKey": "CC", "chsName": "科科斯群岛", "enName": "Cocos Islands", "pyFirst": "K"},
                          {"areaKey": "KY", "chsName": "开曼群岛", "enName": "Cayman Islands", "pyFirst": "K"},
                          {"areaKey": "QA", "chsName": "卡塔尔", "enName": "Qatar", "pyFirst": "K"},
                          {"areaKey": "AZ", "chsName": "阿塞拜疆", "enName": "Azerbaijan", "pyFirst": "A"},
                          {"areaKey": "HN", "chsName": "洪都拉斯", "enName": "Honduras", "pyFirst": "H"},
                          {"areaKey": "AW", "chsName": "阿鲁巴岛", "enName": "Aruba", "pyFirst": "A"},
                          {"areaKey": "KH", "chsName": "柬埔寨", "enName": "Cambodia", "pyFirst": "J"},
                          {"areaKey": "CO", "chsName": "哥伦比亚", "enName": "Colombia", "pyFirst": "G"},
                          {"areaKey": "IR", "chsName": "伊朗", "enName": "Iran", "pyFirst": "Y"},
                          {"areaKey": "ZA", "chsName": "南非", "enName": "South Africa", "pyFirst": "N"},
                          {"areaKey": "UY", "chsName": "乌拉圭", "enName": "Uruguay", "pyFirst": "W"},
                          {"areaKey": "GU", "chsName": "关岛", "enName": "Guam", "pyFirst": "G"},
                          {"areaKey": "GH", "chsName": "加纳", "enName": "Ghana", "pyFirst": "J"},
                          {"areaKey": "GN", "chsName": "几内亚", "enName": "Guynea", "pyFirst": "J"},
                          {"areaKey": "MH", "chsName": "马绍尔群岛", "enName": "Marshall Islands",
                           "pyFirst": "M"},
                          {"areaKey": "SE", "chsName": "瑞典", "enName": "Sweden", "pyFirst": "R"},
                          {"areaKey": "SB", "chsName": "所罗门群岛", "enName": "Solomon Islands",
                           "pyFirst": "S"},
                          {"areaKey": "NE", "chsName": "尼日尔", "enName": "Niger", "pyFirst": "N"},
                          {"areaKey": "HT", "chsName": "海地", "enName": "Haiti", "pyFirst": "H"},
                          {"areaKey": "PL", "chsName": "波兰", "enName": "Poland", "pyFirst": "B"},
                          {"areaKey": "DO", "chsName": "多米尼加共和国", "enName": "Dominican Republic",
                           "pyFirst": "D"},
                          {"areaKey": "PS", "chsName": "巴勒斯坦", "enName": "Palestine", "pyFirst": "B"},
                          {"areaKey": "KW", "chsName": "科威特", "enName": "Kuwait", "pyFirst": "K"},
                          {"areaKey": "UZ", "chsName": "乌兹别克斯坦", "enName": "Republic of Uzbekistan",
                           "pyFirst": "W"},
                          {"areaKey": "GD", "chsName": "格林纳达", "enName": "Grenada", "pyFirst": "G"},
                          {"areaKey": "KG", "chsName": "吉尔吉斯斯坦", "enName": "Kyrgyzstan", "pyFirst": "J"},
                          {"areaKey": "JO", "chsName": "约旦", "enName": "Jordan", "pyFirst": "Y"},
                          {"areaKey": "IL", "chsName": "以色列", "enName": "Israel", "pyFirst": "Y"},
                          {"areaKey": "UK", "chsName": "英国", "enName": "United Kingdom", "pyFirst": "Y"},
                          {"areaKey": "MW", "chsName": "马拉维", "enName": "Malawi", "pyFirst": "M"},
                          {"areaKey": "MC", "chsName": "摩纳哥", "enName": "Monaco", "pyFirst": "M"},
                          {"areaKey": "IC", "chsName": "加那利群岛", "enName": "Canary Islands", "pyFirst": "J"},
                          {"areaKey": "JM", "chsName": "牙买加", "enName": "Jamaica", "pyFirst": "Y"},
                          {"areaKey": "MP", "chsName": "北马里亚纳群岛", "enName": "The Northern Mariana Islands",
                           "pyFirst": "B"},
                          {"areaKey": "BH", "chsName": "巴林岛", "enName": "Bahrain", "pyFirst": "B"},
                          {"areaKey": "MK", "chsName": "马其顿", "enName": "Macedonia", "pyFirst": "M"},
                          {"areaKey": "ET", "chsName": "埃塞俄比亚", "enName": "Ethiopia", "pyFirst": "A"},
                          {"areaKey": "CL", "chsName": "智利", "enName": "Chile", "pyFirst": "Z"},
                          {"areaKey": "GP", "chsName": "瓜德罗普岛", "enName": "Guadeloupe", "pyFirst": "G"},
                          {"areaKey": "FK", "chsName": "福克兰群岛", "enName": "Falkland Islands",
                           "pyFirst": "F"},
                          {"areaKey": "GL", "chsName": "格陵兰", "enName": "Greenland", "pyFirst": "G"},
                          {"areaKey": "BF", "chsName": "布基纳法索", "enName": "Burkina Faso", "pyFirst": "B"},
                          {"areaKey": "GI", "chsName": "直布罗陀", "enName": "Gibraltar", "pyFirst": "Z"},
                          {"areaKey": "MV", "chsName": "马尔代夫", "enName": "Maldives", "pyFirst": "M"},
                          {"areaKey": "CU", "chsName": "古巴", "enName": "Cuba", "pyFirst": "G"},
                          {"areaKey": "LS", "chsName": "莱索托", "enName": "Lesotho", "pyFirst": "L"},
                          {"areaKey": "MA", "chsName": "摩洛哥", "enName": "Morocco", "pyFirst": "M"},
                          {"areaKey": "AL", "chsName": "阿尔巴尼亚", "enName": "Albania", "pyFirst": "A"},
                          {"areaKey": "AF", "chsName": "阿富汗", "enName": "Afghanistan", "pyFirst": "A"},
                          {"areaKey": "CA", "chsName": "加拿大", "enName": "Canada", "pyFirst": "J"},
                          {"areaKey": "BB", "chsName": "巴巴多斯", "enName": "Barbados", "pyFirst": "B"},
                          {"areaKey": "LC", "chsName": "圣卢西亚岛", "enName": "Saint Lucia", "pyFirst": "S"},
                          {"areaKey": "PN", "chsName": "皮特克恩岛", "enName": "Pitcairn Island",
                           "pyFirst": "P"},
                          {"areaKey": "LV", "chsName": "拉脱维亚", "enName": "Latvia", "pyFirst": "L"},
                          {"areaKey": "NO", "chsName": "挪威", "enName": "Norway", "pyFirst": "N"},
                          {"areaKey": "BE", "chsName": "比利时", "enName": "Belgium", "pyFirst": "B"},
                          {"areaKey": "VE", "chsName": "委内瑞拉", "enName": "Venezuela", "pyFirst": "W"},
                          {"areaKey": "MQ", "chsName": "马提尼克", "enName": "Martinique", "pyFirst": "M"},
                          {"areaKey": "GY", "chsName": "圭亚那", "enName": "Guyana", "pyFirst": "G"},
                          {"areaKey": "AM", "chsName": "亚美尼亚", "enName": "Armenia", "pyFirst": "Y"},
                          {"areaKey": "EC", "chsName": "厄瓜多尔", "enName": "Ecuador", "pyFirst": "E"},
                          {"areaKey": "CV", "chsName": "佛得角", "enName": "Cape Verde", "pyFirst": "F"},
                          {"areaKey": "NZ", "chsName": "新西兰", "enName": "New Zealand", "pyFirst": "X"},
                          {"areaKey": "RO", "chsName": "罗马尼亚", "enName": "Romania", "pyFirst": "L"},
                          {"areaKey": "DM", "chsName": "多米尼加", "enName": "Dominica", "pyFirst": "D"},
                          {"areaKey": "TZ", "chsName": "坦桑尼亚", "enName": "Tanzania", "pyFirst": "T"},
                          {"areaKey": "BD", "chsName": "孟加拉国", "enName": "Bangladesh", "pyFirst": "M"},
                          {"areaKey": "TD", "chsName": "乍得", "enName": "Chad", "pyFirst": "Z"},
                          {"areaKey": "LT", "chsName": "立陶宛", "enName": "Lithuania", "pyFirst": "L"},
                          {"areaKey": "TJ", "chsName": "塔吉克斯坦", "enName": "Tajikistan", "pyFirst": "T"},
                          {"areaKey": "TK", "chsName": "托克劳", "enName": "Tokelau", "pyFirst": "T"},
                          {"areaKey": "BS", "chsName": "巴哈马群岛", "enName": "Bahamas", "pyFirst": "B"},
                          {"areaKey": "MM", "chsName": "缅甸", "enName": "Myanmar", "pyFirst": "M"},
                          {"areaKey": "BI", "chsName": "布隆迪", "enName": "Burundi", "pyFirst": "B"},
                          {"areaKey": "PY", "chsName": "巴拉圭", "enName": "Paraguay", "pyFirst": "B"},
                          {"areaKey": "SK", "chsName": "斯洛伐克", "enName": "Slovakia", "pyFirst": "S"},
                          {"areaKey": "FI", "chsName": "芬兰", "enName": "Finland", "pyFirst": "F"},
                          {"areaKey": "GA", "chsName": "加蓬", "enName": "Gabon", "pyFirst": "J"},
                          {"areaKey": "DZ", "chsName": "阿尔及利亚", "enName": "Algeria", "pyFirst": "A"},
                          {"areaKey": "FO", "chsName": "法罗群岛", "enName": "Faroe Islands", "pyFirst": "F"},
                          {"areaKey": "ZM", "chsName": "赞比亚", "enName": "Zambia", "pyFirst": "Z"},
                          {"areaKey": "NU", "chsName": "纽埃", "enName": "Niue", "pyFirst": "N"},
                          {"areaKey": "ER", "chsName": "厄立特里亚国", "enName": "Eritrea", "pyFirst": "E"},
                          {"areaKey": "HK", "chsName": "香港", "enName": "Hong Kong", "pyFirst": "X"},
                          {"areaKey": "IT", "chsName": "意大利", "enName": "Italy", "pyFirst": "Y"},
                          {"areaKey": "MS", "chsName": "蒙特色拉特岛", "enName": "Montserrat", "pyFirst": "M"},
                          {"areaKey": "EE", "chsName": "爱沙尼亚", "enName": "Estonia", "pyFirst": "A"},
                          {"areaKey": "WS", "chsName": "萨摩亚", "enName": "Samoa", "pyFirst": "S"},
                          {"areaKey": "TG", "chsName": "多哥", "enName": "Togo", "pyFirst": "D"},
                          {"areaKey": "ML", "chsName": "马里", "enName": "Mali", "pyFirst": "M"},
                          {"areaKey": "GF", "chsName": "法属圭亚那", "enName": "French Guyana", "pyFirst": "F"},
                          {"areaKey": "KM", "chsName": "科摩罗", "enName": "Comoros", "pyFirst": "K"},
                          {"areaKey": "ID", "chsName": "印度尼西亚", "enName": "Indonesia", "pyFirst": "Y"},
                          {"areaKey": "KE", "chsName": "肯尼亚", "enName": "Kenya", "pyFirst": "K"},
                          {"areaKey": "EG", "chsName": "埃及", "enName": "Egypt", "pyFirst": "A"},
                          {"areaKey": "NF", "chsName": "诺福克岛", "enName": "Norfolk Island", "pyFirst": "N"},
                          {"areaKey": "RS", "chsName": "塞尔维亚", "enName": "Serbia", "pyFirst": "S"},
                          {"areaKey": "TR", "chsName": "土耳其", "enName": "Turkey", "pyFirst": "T"},
                          {"areaKey": "DK", "chsName": "丹麦", "enName": "Denmark", "pyFirst": "D"},
                          {"areaKey": "AD", "chsName": "安道尔", "enName": "Andorra", "pyFirst": "A"},
                          {"areaKey": "LR", "chsName": "利比里亚", "enName": "Liberia", "pyFirst": "L"},
                          {"areaKey": "AE", "chsName": "阿拉伯联合酋长国", "enName": "United Arab Emirates",
                           "pyFirst": "A"},
                          {"areaKey": "CH", "chsName": "瑞士", "enName": "Switzerland", "pyFirst": "R"},
                          {"areaKey": "AU", "chsName": "澳大利亚", "enName": "Australia", "pyFirst": "A"},
                          {"areaKey": "TP", "chsName": "东帝汶", "enName": "East Timor", "pyFirst": "D"},
                          {"areaKey": "LY", "chsName": "利比亚", "enName": "Libya", "pyFirst": "L"},
                          {"areaKey": "RW", "chsName": "卢旺达", "enName": "Rwanda", "pyFirst": "L"},
                          {"areaKey": "SA", "chsName": "沙特阿拉伯", "enName": "Saudi Arabia", "pyFirst": "S"},
                          {"areaKey": "AR", "chsName": "阿根廷", "enName": "Argentina", "pyFirst": "A"},
                          {"areaKey": "GM", "chsName": "冈比亚", "enName": "Gambia", "pyFirst": "G"},
                          {"areaKey": "BY", "chsName": "白俄罗斯", "enName": "Belarus", "pyFirst": "B"},
                          {"areaKey": "SL", "chsName": "塞拉利昂", "enName": "Sierra Leone", "pyFirst": "S"},
                          {"areaKey": "TM", "chsName": "土库曼斯坦", "enName": "Turkmenistan", "pyFirst": "T"},
                          {"areaKey": "AG", "chsName": "安提瓜和巴布达", "enName": "Antigua and Barbuda",
                           "pyFirst": "A"},
                          {"areaKey": "MR", "chsName": "毛里塔尼亚", "enName": "Mauritania", "pyFirst": "M"},
                          {"areaKey": "PT", "chsName": "葡萄牙", "enName": "Portugal", "pyFirst": "P"},
                          {"areaKey": "BW", "chsName": "博茨瓦纳", "enName": "Botswana", "pyFirst": "B"},
                          {"areaKey": "GT", "chsName": "危地马拉", "enName": "Guatemala", "pyFirst": "W"},
                          {"areaKey": "BT", "chsName": "不丹", "enName": "Bhutan", "pyFirst": "B"},
                          {"areaKey": "AI", "chsName": "安圭拉岛", "enName": "Anguilla", "pyFirst": "A"},
                          {"areaKey": "OM", "chsName": "阿曼", "enName": "Oman", "pyFirst": "A"},
                          {"areaKey": "KI", "chsName": "基里巴斯", "enName": "Kiribati", "pyFirst": "J"},
                          {"areaKey": "UA", "chsName": "乌克兰", "enName": "Ukraine", "pyFirst": "W"},
                          {"areaKey": "YE", "chsName": "也门", "enName": "Yemen", "pyFirst": "Y"},
                          {"areaKey": "DR", "chsName": "刚果民主共和国",
                           "enName": "Democratic Republic of the Congo", "pyFirst": "G"},
                          {"areaKey": "MD", "chsName": "摩尔多瓦", "enName": "Moldova", "pyFirst": "M"},
                          {"areaKey": "GW", "chsName": "几内亚比绍", "enName": "Guinea-Bissau", "pyFirst": "J"},
                          {"areaKey": "CG", "chsName": "刚果布共和国", "enName": "Congo Brazzaville",
                           "pyFirst": "G"},
                          {"areaKey": "SN", "chsName": "塞内加尔", "enName": "Senegal", "pyFirst": "S"},
                          {"areaKey": "BA", "chsName": "波黑", "enName": "Bosnia Hercegovina",
                           "pyFirst": "B"},
                          {"areaKey": "MO", "chsName": "澳门", "enName": "Macao", "pyFirst": "A"},
                          {"areaKey": "KN", "chsName": "圣基茨和尼维斯", "enName": "Saint Kitts and Nevis",
                           "pyFirst": "S"},
                          {"areaKey": "TO", "chsName": "汤加", "enName": "Tonga", "pyFirst": "T"},
                          {"areaKey": "NG", "chsName": "尼日利亚", "enName": "Nigeria", "pyFirst": "N"},
                          {"areaKey": "TT", "chsName": "特立尼达和多巴哥", "enName": "Trinidad and Tobago",
                           "pyFirst": "T"},
                          {"areaKey": "CF", "chsName": "中非共和国", "enName": "Central African Republic",
                           "pyFirst": "Z"},
                          {"areaKey": "PE", "chsName": "秘鲁", "enName": "Peru", "pyFirst": "M"},
                          {"areaKey": "PG", "chsName": "巴布亚新几内亚", "enName": "Papua New Guinea",
                           "pyFirst": "B"},
                          {"areaKey": "CX", "chsName": "圣延岛", "enName": "Christmas Island", "pyFirst": "S"},
                          {"areaKey": "AN", "chsName": "安的列斯", "enName": "Netherlands Antilles",
                           "pyFirst": "A"},
                          {"areaKey": "BO", "chsName": "玻利维亚", "enName": "Bolivia", "pyFirst": "B"},
                          {"areaKey": "IQ", "chsName": "伊拉克", "enName": "Iraq", "pyFirst": "Y"},
                          {"areaKey": "NP", "chsName": "尼泊尔", "enName": "Nepal", "pyFirst": "N"},
                          {"areaKey": "BJ", "chsName": "贝宁", "enName": "Benin", "pyFirst": "B"},
                          {"areaKey": "VN", "chsName": "越南", "enName": "Vietnam", "pyFirst": "Y"},
                          {"areaKey": "NI", "chsName": "尼加拉瓜", "enName": "Nicaragua", "pyFirst": "N"},
                          {"areaKey": "PW", "chsName": "帕劳群岛", "enName": "Palau", "pyFirst": "P"},
                          {"areaKey": "SO", "chsName": "索马里", "enName": "Somalia", "pyFirst": "S"},
                          {"areaKey": "SM", "chsName": "圣马力诺", "enName": "San Marino", "pyFirst": "S"},
                          {"areaKey": "NR", "chsName": "瑙鲁", "enName": "Nauru", "pyFirst": "N"},
                          {"areaKey": "BN", "chsName": "文莱", "enName": "Brunei Darussalam", "pyFirst": "W"},
                          {"areaKey": "MZ", "chsName": "莫桑比克", "enName": "Mozambique", "pyFirst": "M"},
                          {"areaKey": "GR", "chsName": "希腊", "enName": "Greece", "pyFirst": "X"},
                          {"areaKey": "TN", "chsName": "突尼斯", "enName": "Tunisia", "pyFirst": "T"},
                          {"areaKey": "RU", "chsName": "俄罗斯", "enName": "Russian Federation",
                           "pyFirst": "E"},
                          {"areaKey": "MG", "chsName": "马达加斯加岛", "enName": "Madagascar", "pyFirst": "M"},
                          {"areaKey": "NA", "chsName": "纳米比亚", "enName": "Namibia", "pyFirst": "N"},
                          {"areaKey": "CQ", "chsName": "赤道几内亚", "enName": "Equatorial Guinea",
                           "pyFirst": "C"},
                          {"areaKey": "SR", "chsName": "苏里南", "enName": "Suriname", "pyFirst": "S"},
                          {"areaKey": "MU", "chsName": "毛里求斯", "enName": "Mauritius", "pyFirst": "M"},
                          {"areaKey": "LA", "chsName": "老挝", "enName": "Laos", "pyFirst": "L"},
                          {"areaKey": "US", "chsName": "美国", "enName": "United States", "pyFirst": "M"},
                          {"areaKey": "ST", "chsName": "圣多美与普林希比共和国", "enName": "Sao Tome and Principe",
                           "pyFirst": "S"},
                          {"areaKey": "BM", "chsName": "百慕大群岛", "enName": "Bermuda", "pyFirst": "B"},
                          {"areaKey": "LU", "chsName": "卢森堡", "enName": "Luxembourg", "pyFirst": "L"},
                          {"areaKey": "CR", "chsName": "哥斯达黎加", "enName": "Costa Rica", "pyFirst": "G"},
                          {"areaKey": "KR", "chsName": "韩国", "enName": "South Korea", "pyFirst": "H"},
                          {"areaKey": "CZ", "chsName": "捷克", "enName": "Czech Republic", "pyFirst": "J"},
                          {"areaKey": "MX", "chsName": "墨西哥", "enName": "Mexico", "pyFirst": "M"},
                          {"areaKey": "SH", "chsName": "圣赫勒拿岛", "enName": "St Helena", "pyFirst": "S"},
                          {"areaKey": "AO", "chsName": "安哥拉", "enName": "Angola", "pyFirst": "A"},
                          {"areaKey": "MN", "chsName": "蒙古", "enName": "Mongolia", "pyFirst": "M"},
                          {"areaKey": "VC", "chsName": "圣文森特和格林纳丁斯",
                           "enName": "Saint Vincent and the Grenadines", "pyFirst": "S"},
                          {"areaKey": "PH", "chsName": "菲律宾", "enName": "Philippines", "pyFirst": "F"},
                          {"areaKey": "SC", "chsName": "塞舌尔", "enName": "Seychelles", "pyFirst": "S"},
                          {"areaKey": "CK", "chsName": "库克群岛", "enName": "Cook Islands", "pyFirst": "K"},
                          {"areaKey": "PK", "chsName": "巴基斯坦", "enName": "Pakistan", "pyFirst": "B"},
                          {"areaKey": "HR", "chsName": "克罗地亚", "enName": "Croatia", "pyFirst": "K"},
                          {"areaKey": "TH", "chsName": "泰国", "enName": "Thailand", "pyFirst": "T"},
                          {"areaKey": "SI", "chsName": "斯洛文尼亚", "enName": "Slovenia", "pyFirst": "S"},
                          {"areaKey": "VG", "chsName": "英属维尔京群岛", "enName": "British Virgin Islands",
                           "pyFirst": "Y"},
                          {"areaKey": "SY", "chsName": "阿拉伯叙利亚共和国", "enName": "Syrian Arab Republic",
                           "pyFirst": "A"},
                          {"areaKey": "CY", "chsName": "塞浦路斯", "enName": "Cyprus", "pyFirst": "S"},
                          {"areaKey": "BR", "chsName": "巴西", "enName": "Brazil", "pyFirst": "B"},
                          {"areaKey": "LB", "chsName": "黎巴嫩", "enName": "Lebanon", "pyFirst": "L"},
                          {"areaKey": "IS", "chsName": "冰岛", "enName": "Iceland", "pyFirst": "B"},
                          {"areaKey": "PA", "chsName": "巴拿马", "enName": "Panama", "pyFirst": "B"},
                          {"areaKey": "FM", "chsName": "密克罗尼西亚", "enName": "Micronesia", "pyFirst": "M"},
                          {"areaKey": "VA", "chsName": "梵蒂冈", "enName": "Vatican City State",
                           "pyFirst": "F"},
                          {"areaKey": "NC", "chsName": "新喀里多尼亚", "enName": "New Caledonia", "pyFirst": "X"},
                          {"areaKey": "MT", "chsName": "马尔他", "enName": "Malta", "pyFirst": "M"},
                          {"areaKey": "BG", "chsName": "保加利亚", "enName": "Bulgaria", "pyFirst": "B"},
                          {"areaKey": "ES", "chsName": "西班牙", "enName": "Spain", "pyFirst": "X"},
                          {"areaKey": "CI", "chsName": "象牙海岸", "enName": "Ivory Coast", "pyFirst": "X"},
                          {"areaKey": "IE", "chsName": "爱尔兰", "enName": "Ireland", "pyFirst": "A"},
                          {"areaKey": "BZ", "chsName": "伯利兹城", "enName": "Belize", "pyFirst": "B"},
                          {"areaKey": "SZ", "chsName": "斯威士兰", "enName": "Swaziland", "pyFirst": "S"},
                          {"areaKey": "SV", "chsName": "萨尔瓦多", "enName": "EI Salvador", "pyFirst": "S"},
                          {"areaKey": "GE", "chsName": "格鲁吉亚", "enName": "Georgia", "pyFirst": "G"},
                          {"areaKey": "SD", "chsName": "苏丹", "enName": "Sudan", "pyFirst": "S"},
                          {"areaKey": "PR", "chsName": "波多黎各", "enName": "Puerto Rico", "pyFirst": "B"},
                          {"areaKey": "FJ", "chsName": "斐济", "enName": "Fiji", "pyFirst": "F"},
                          {"areaKey": "NL", "chsName": "荷兰", "enName": "Netherlands", "pyFirst": "H"},
                          {"areaKey": "UG", "chsName": "乌干达", "enName": "Uganda", "pyFirst": "W"},
                          {"areaKey": "HU", "chsName": "匈牙利", "enName": "Hungary", "pyFirst": "X"},
                          {"areaKey": "TC", "chsName": "特克斯和凯科斯群岛", "enName": "Turks and Caicos Islands",
                           "pyFirst": "T"}]}
