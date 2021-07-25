from Crypto.Cipher import AES
import base64
import msgpack
import re
import os
from satrokiapi import WebClient

def decrypt(encrypted):
    mode = AES.MODE_CBC
    ss2 = base64.b64decode(encrypted)
    vi = b'ha4nBYA2APUD6Uv1'
    key = ss2[-32:]
    ss2 = ss2[:-32]
    cryptor=AES.new(key,mode,vi)
    plain_text  = cryptor.decrypt(ss2)
    try:
        return msgpack.unpackb(plain_text[:-plain_text[-1]],
                strict_map_key = False)
    except msgpack.ExtraData as err:
        return err.unpacked
    except:
        return {"data_headers" : {}, "data" : {}}

def unit_trans():
    filein = ''.join(open('load.xml','r').readlines())
    cdata = re.findall(r'CDATA\[.+\]', filein)
    data_res = base64.b64decode(bytes(cdata[4][6:-2], encoding='utf-8'))
    data_list = decrypt(re.split(b'\r\n\r\n',data_res)[-1])['data']
    id_list = []
    unit_list = []
    for data in data_list['unit_list']:
        id_list.append(data['id'])
        data_dict = {
            "unitId": data['id'],
            "level": data['unit_level'],
            "rarity": data['unit_rarity'],
            "promotion": data['promotion_level']
        }
        if data['unique_equip_slot']:
            if data['unique_equip_slot'][0]['is_slot']:
                data_dict["uniqueEquipRank"] = data['unique_equip_slot'][0]['enhancement_level']
        for i in range(6):
            if data['equip_slot'][i]['is_slot'] == 1:
                data_dict["slot"+str(i+1)] = True
        unit_list.append(data_dict)
    for chara in data_list['user_chara_info']:
        unitid = chara['chara_id'] * 100 + 1
        for i in unit_list:
            if i['unitId'] == unitid:
                i["loveLevel"] = chara['love_level']
    for piece in data_list['item_list']:
        if piece['id'] > 31000 and piece['id'] < 31999:
            unitid = (piece['id'] - 30000) * 100 + 1
        for i in unit_list:
            if i['unitId'] == unitid:
                i["pieces"] = piece['stock']
    return id_list, unit_list

def equip_trans():
    filein = ''.join(open('load.xml','r').readlines())
    cdata = re.findall(r'CDATA\[.+\]', filein)
    data_res = base64.b64decode(bytes(cdata[4][6:-2], encoding='utf-8'))
    line = decrypt(re.split(b'\r\n\r\n',data_res)[-1])
    data_list = line['data']['user_equip']
    item_list = []
    for item in data_list:
        item_list.append({"eId": item['id'], "stock": item['stock']})
    return item_list

# 添加全部角色
def unit_addall():
    id_list = unit_trans()[0]
    client = WebClient()
    client.GetBox()
    box_pre = []
    for chara in client.box_list:
        if chara['id']:
            box_pre.append(chara['id'])
    client.DeleteUser(box_pre)
    client.AddUser(id_list)

#修改全部角色
def unit_editall():
    unit_list = unit_trans()[1]
    client = WebClient()
    client.GetBox()
    for unit_dict in unit_list:
        client.EditUserBox(unit_dict)
        print("已完成更新角色" + str(unit_dict["unitId"]))

def equip_addall():
    equip_list = equip_trans()
    client = WebClient()
    client.SaveEquipStock(equip_list)

if __name__ == "__main__":
    unit_addall()
    unit_editall()
    equip_addall()