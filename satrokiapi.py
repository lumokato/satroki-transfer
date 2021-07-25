import requests
from Crypto.Cipher import AES
import base64
import msgpack
import time
import csv
import json
class WebClient:
    def __init__(self):
        self.urlroot = "https://pci.satroki.tech/"
        self.default_headers={
            "Host": "pci.satroki.tech",
            "Accept-Encoding": "gzip, deflate",
            "Authorization": "",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            "Content-Type": "application/json; charset=utf-8",
            "Origin": "https://pci.satroki.tech",
            "Sec-Ch-Ua": "Chromium",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://pci.satroki.tech/",
            "Accept-Language": "zh-CN,zh",
            "Accept": "*/*",
            "Connection": "close"
            }
        self.conn = requests.session()
        self.Login()

    def PostApi(self, apiurl, request):
        headers = self.default_headers
        resp = self.conn.post(url= self.urlroot + apiurl,
                        headers = headers, json = request)
        try:
            ret = json.loads(resp.content.decode())
        except:
            ret = None
        return ret

    def GetApi(self, apiurl):
        headers = self.default_headers
        resp = self.conn.get(url= self.urlroot + apiurl,
                        headers = headers)
        ret = json.loads(resp.content.decode())
        return ret

    def PutApi(self, apiurl, request):
        headers = self.default_headers
        resp = self.conn.put(url= self.urlroot + apiurl,
                        headers = headers, json = request)
        try:
            ret = json.loads(resp.content.decode())
        except:
            ret = None
        return ret

    def Login(self, username = "hego", password = "111111"):
        ret = self.PostApi('api/Login', {"userName": username, "password": password,"newPassword": "","email": "","nickName": ""})
        self.default_headers["Authorization"] = 'Bearer '+ ret['token']

    def GetBox(self):
        self.box_list = self.GetApi('api/Box/GetUserBoxResult?s=cn&mr=13&ms=4&ma=True')["box"]
    
    def AddUser(self, unitid_list: list):
        resp = self.PostApi('api/Box/AddUserBoxLines?s=cn', unitid_list)
        self.box_list = resp

    def DeleteUser(self, id_list: list):
        self.PostApi('api/Box/DeleteUserBoxLines', id_list)

    def GetUnitSource(self, unitid: int, pro_level: int):
        equip_list = self.GetApi('api/Unit/GetUnitSourceData/' + str(unitid))["unitPromotions"]
        for equip in equip_list:
            if equip["promotionLevel"] == pro_level:
                return equip

    def EditUserBox(self, unit_dict):
        for unit in self.box_list:
            if unit["unitId"] == unit_dict["unitId"]:
                req = unit
        req.update(unit_dict)
        if 'uniqueEquipRank' in req.keys():
            req["targetUniqueEquipRank"] = req['uniqueEquipRank']
        if 'rarity' in req.keys():
            req["targetRarity"] = req['rarity']
        req["targetLoveLevel"] = 8
        req["unitPromotion"] = self.GetUnitSource(req["unitId"], req['promotion'])
        if req["targetPromotion"] == 1:
            req["targetPromotion"] = 13
        self.PutApi('api/Box/EditUserBoxLine?mr=13&ms=4&ma=True', req)

    def SaveEquipStock(self, stock_list):
        self.PostApi('api/Equipment/SaveUserEquipStock?s=cn', {"id":0,"userId":0,"server":"cn","stocks": stock_list})
