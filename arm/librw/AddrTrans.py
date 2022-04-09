#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import copy

class AddrTrans:
    def __init__(self, fpath):
        self.file_path = fpath
        self.flist = []
        self.load_fille(self.file_path)

    def load_fille(self, fpath):
        with open(fpath, "r") as f:
            self.flist = json.load(f)

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
            func_info = flist.get(str(add), None)
            if func_info is None:
                continue
            sz = func_info.get("sz", -1)
            if sz < 0:
                print("add = %s, size = %s" % (add, sz))
                continue
            # 从获得当前地址映射的地址值，如果不存在映射，地址还是他本身
            add_start = add_map.get(add, add)
            # 字节序，ELF可以获得，其他逻辑也要变，这里先做一个提醒，默认从小到大
            if is_asc:
                # 存储地址，从小到大
                add_end = add_start + sz
            else:
                # 存储地址，由大到小
                add_end = add_start - sz

            if i == len(add_list) - 1:
                # last one
                break

            # 下一个地址
            # 地址区间，like [1,10).
            add_next = add_list[i + 1]
            if add_end > add_next:
                # 当前一个地址的end 大于 大于地址的 start
                add_map[add_next] = add_end
                diff_ins.append({"index": i, "info": "add = %s, sz =%s, add_next = %s, add_end = %s" % (add, sz, add_next, add_end)})
            else:
                #
                add_map[add_next] = add_next

        for add in add_list:
            adjust_flist[str(add_map.get(add, add))] = flist.get(str(add))

        t_add_list = []
        for i in adjust_flist.keys():
            t_add_list.append(int(i))
        t_add_list.sort(reverse=False)
        print(t_add_list)
        print("after adjust, len(adjust_flist) = ", len(adjust_flist))
        print(diff_ins)
        with open("adjust_flist.txt", "w") as f:
            json.dump(adjust_flist, f)
        return adjust_flist

if __name__ == "__main__":
    ad = AddrTrans("flist.txt")
    ad.func_adjust(ad.flist)