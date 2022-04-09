#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import copy


class SizeTrans:
    def __init__(self):
            pass

    def func_adjust(self, flist, is_asc=True):
        # 每次，排序，获得两个只计算两个。
        add_list = []
        diff_ins = []
        for i in flist.keys():
            add_list.append(int(i))

        # 降序
        add_list.sort(reverse=False)
        # 新旧地址值映射
        add_map = dict()
        # 重构地址
        adjust_flist = dict()

        print("before adjust, len(flist) = ", len(flist))
        print(add_list)
        for i in range(len(add_list)):
            add = add_list[i]
            func_info = flist.get(add, None)
            if func_info is None:
                continue
            sz = func_info.get("sz", -1)
            if sz < 0:
                print("add = %s, size = %s" % (add, sz))
                continue
            # 从获得当前地址映射的地址值，如果不存在映射，地址还是他本身
            # 字节序，ELF可以获得，其他逻辑也要变，这里先做一个提醒，默认从小到大
            if is_asc:
                # 存储地址，从小到大
                add_end = add + sz
            else:
                # 存储地址，由大到小
                add_end = add - sz

            if i == len(add_list) - 1:
                # last one
                break

            # 下一个地址
            # 地址区间，like [1,10).
            add_next = add_list[i + 1]
            next_func_info = flist.get(add_next)
            if add_end > add_next:
                # 当前一个地址的end 大于 大于地址的 start
                # 函数A的size应该是函数B的Size减去函数A的size
                new_func_info = copy.deepcopy(func_info)
                new_func_info["sz"] = add_next - add
                flist[add] = new_func_info
                if new_func_info["sz"] < 0:
                    diff_ins.append("new_func_sz: %s,  A: start= %s, sz = %s, b: start = %s, sz= %s " % (new_func_info["sz"], add, func_info["sz"], add_next, next_func_info["sz"]))
            else:
                #
                add_map[add_next] = add_next

        print("after adjust, len(flist) = ", len(flist))
        print(diff_ins)
        with open("adjus_size_flist.txt", "w") as f:
            json.dump(flist, f)
        for i in diff_ins:
            print(i)
        return flist

if __name__ == "__main__":
    ad = SizeTrans()
    flist = {}
    with open("flist.txt", "r") as f:
        flist = json.load(f)
    t = {}
    for k, v in flist.items():
        t[int(k)] = v
    ad.func_adjust(t)