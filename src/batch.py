import time

from __init__ import *
from db import *
from invite import copy_invitation
from send_msg import *

is_doing = False


def end_batch():
    global is_doing
    is_doing = False


def batch_msg(nation: str, categorys, msg: str, current_user:str,min_fan_num: int):
    global is_doing
    if not is_doing:
        is_doing = True
    else:
        return

    addlog("开始批量给达人发消息")
    # 数据库读取达人信息
    try:
        creators = get_creator(nation)
        for creator in creators.values():
            if not is_doing:
                return

            if int(creator["fans"]) < min_fan_num:
                continue

            is_target = False
            for category in categorys:
                if category in creator["category"]:
                    is_target = True
                    break
            if not is_target:
                #print(creator["name"], "非目标达人")
                continue

            if get_send_msg_time(creator["name"], nation, current_user) != "":
                continue

            addlog("发消息给达人:" + creator["name"] + "站点" + nation)
            # 发送邀请
            # if copy_invitation(creator[0]):
            # 没有发送过消息
            if send_msg(creator["name"], nation, msg, current_user):
                update_send_msg(creator["name"], nation, current_user)
            time.sleep(1)
    except Exception as e:
        print(e)
    is_doing = False


def batch_invite(nation: str, categorys, sample_id, current_user,min_fan_num: int):
    global is_doing
    if not is_doing:
        is_doing = True
    else:
        return

    addlog("开始批量邀请达人")

    creators = []
    for creator in get_creator(nation).values():
        if int(creator["fans"]) < min_fan_num:
            continue
        is_target = False
        for category in categorys:
            if category in creator["category"]:
                is_target = True
                break
        if not is_target:
            continue

        print(creator["name"], "目标达人", )
        creators.append(creator)

        if get_invite_time(creator["name"], nation, current_user) != "":
            continue

    # 10个一组
    groups = [creators[i:i + 45] for i in range(0, len(creators), 45)]
    print(len(groups), len(creators))

    # 数据库读取达人信息
    try:
        for group in groups:
            print("小组1")
            # 发送邀请
            copy_invitation(group, sample_id, nation)
            for creator in group:
                update_invite(creator["name"], nation, current_user)
    except Exception as e:
        print(e)
    is_doing = False

