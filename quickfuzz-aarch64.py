#!/usr/bin/env python3

import argparse
import json
import tempfile
import subprocess
import os
import sys
import traceback
import importlib
from arm.librw.AddrTrans import AddrTrans
from arm.librw.sizeTrans import SizeTrans
import re
import copy


def gen_table_file(source_file):
    save_table = source_file + ".table"
    cmd = "readelf -Ws {0} > {1}".format(source_file, save_table)
    cmd_out = os.popen(cmd).readlines()
    print(cmd_out)
    print(save_table)
    return save_table


def gen_same_functions(file_path, title_index=0, content_index=1, terminal_flages=["Symbol table", ".symtab"]):
    """
        file_path,
        title_index : 文件名
        content_index: 正文
    """
    functions = []
    titl_linses = ""
    save_path = file_path + ".out"

    source_lines = []
    dump_lines = []
    with open(file_path, "r") as f:
        source_lines = f.readlines()
    if len(source_lines) == 0 or len(source_lines) < content_index:
        return False, "source line count is %s" % (len(source_lines))
    title_line = source_lines[title_index]
    content_lines = source_lines[content_index: len(source_lines)]
    # print(title_line, content_lines)
    info_dict = {}
    for line in content_lines:
        if len([f for f in terminal_flages if f in line]) == len(terminal_flages):
            break
        f = re.search("^\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)\n", line)
        if f is None:
            print("abnormal line \n", line, len(content_lines), content_lines.index(line))
            continue
        gps = f.groups()
        try:
            if int(gps[2]) == 0:
                # 长度为零的跑去
                continue
        except:
            print("abnormal line 2 \n", line, len(content_lines), content_lines.index(line))
            continue

        k = "%s_%s_%s_%s_%s_%s" % (gps[1], gps[2], gps[3], gps[4], gps[5], gps[6])
        if k not in info_dict:
            info_dict[k] = []
        info_dict[k].append((gps[0], gps[7]))

    titles = re.search("^\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*)\n", title_line).groups()
    print(titles)
    outlins = []
    outlins.append("\t".join(titles) + '\n')

    for k, vs in info_dict.items():
        if len(vs) <= 1:
            continue
        functions.append(vs)
        for v in vs:
            outlins.append(v[0] + "\t" + "\t".join(k.split("_")) + "\t" + v[1] + "\n")

    with open(save_path, "w") as f:
        f.writelines(outlins)
    return functions

# section注释功能
def section_reset(source_lines, start_flags=[".section", ".init_array"], end_flags=[".section"]):
    format_line = []
    is_start = False
    for each_line in source_lines:
        if is_start is False:
            # 不开始，看是否需要开始
            is_start = len([f for f in start_flags if f in each_line]) == len(start_flags)
        else:
            # 已开始，判断是否结束
            is_start = len([f for f in end_flags if f in each_line]) != len(end_flags)
        
        if is_start is True:
            format_line.append("# %s" % each_line)
        else:
            format_line.append(each_line)

    return format_line

def append_function_to_result(lines, source_file):
    save_file = source_file + ".out"
    # .globl _ZN10ClxDerivedD1Ev
    # .set _ZN10ClxDerivedD1Ev,_ZN10ClxDerivedD2Ev
    # .globl _ZN7ClxBaseD1Ev
    # .set _ZN7ClxBaseD1Ev,_ZN7ClxBaseD2Ev
    # 同一个位置，当前1， 另外一个是二，或者另外一个是二
    append_lines = []
    functions = []

    line_tmp = ".globl {0}\n.set {1},{2}\n" or ".local {0}\n.set {1},{2}\n"
    for line_set in lines:
        # [(num, func), (num, func)]
        funcs = [f[1] for f in line_set]
        if len(funcs) < 2:
            continue
        target = funcs[0]
        # 出现数字的地方，可以递增排序
        for i in range(len(target)):
            try:
                int(target[i])
                index_list = [int(f[i]) for f in funcs]
                index_list = sorted(index_list, reverse=False)
                if (index_list[0] == 1) and (len(index_list) == index_list[len(index_list) - 1]):
                    # 递增，相同
                    functions.append(
                        [target[0:i] + str(tmp_index) + target[i + 1: len(target)] for tmp_index in index_list])
                    break
            except:
                continue
    for sub_funcs in functions:
        append_lines.append(".globl {0}\n".format(sub_funcs[0]))
        append_lines.append(".set {0}\n".format(",".join(sub_funcs)))
    print(append_lines)
    source_lines = []
    with open(source_file, "r") as f:
        source_lines = f.readlines()
    source_lines += append_lines
    with open(save_file, "w") as f:
        f.writelines(source_lines)
    return


def append_function_to_result_2(lines, source_file):
    save_file = source_file + "_asan.s"
    # .globl _ZN10ClxDerivedD1Ev
    # .set _ZN10ClxDerivedD1Ev,_ZN10ClxDerivedD2Ev
    # .globl _ZN7ClxBaseD1Ev
    # .set _ZN7ClxBaseD1Ev,_ZN7ClxBaseD2Ev
    # 同一个位置，当前1， 另外一个是二，或者另外一个是二
    append_lines = []
    append_dict = {}
    functions = []

    line_tmp = ".globl {0}\n.set {1},{2}\n" 
    print("ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ")
    for line_set in lines:
        # [(num, func), (num, func)]
        funcs = [f[1] for f in line_set]
        if len(funcs) < 2:      
            continue
        target = funcs[0]
        # 出现数字的地方，可以递增排序
        for i in range(len(target)):
            try:
                int(target[i])
                index_list = [int(f[i]) for f in funcs]
                index_list = sorted(index_list, reverse=False)
                if (index_list[0] == 1) and (len(index_list) == index_list[len(index_list) - 1]):
                    # 递增，相同
                    functions.append(
                        [target[0:i] + str(tmp_index) + target[i + 1: len(target)] for tmp_index in index_list])
                    break
            except:
                continue
    # 若A和B均存在globle，则跳过；
    # 若A存在globle，B不存在，则添加.globle B 和.set B,A;
    # 若B存在globle，A不存在，则添加.globle A 和.set A,B;
    source_lines = []
    append_lines = []
    with open(source_file, "r") as f:
        source_lines = f.readlines()

    for sub_funcs in functions:
        if len(sub_funcs) !=2:
            continue
        fa = ".globl {0}\n".format(sub_funcs[0])
        fb = ".globl {0}\n".format(sub_funcs[1])
        #fc = ".local {0}\n".format(sub_funcs[0])
        #fd = ".local {0}\n".format(sub_funcs[1])
        sba = ".set {0},{1}\n".format(sub_funcs[1], sub_funcs[0])
        sab = ".set {0},{1}\n".format(sub_funcs[0], sub_funcs[1])
        #sdc = ".set {0},{1}\n".format(sub_funcs[1], sub_funcs[0])
        #scd = ".set {0},{1}\n".format(sub_funcs[0], sub_funcs[1])
        if fa in source_lines and fb in source_lines:
            continue
        #if fc in source_lines and fd in source_lines:
            continue
        elif fa in source_lines and fb not in source_lines:
            append_lines.append(fb)
            append_lines.append(sba)
        elif fa not in source_lines and fb in source_lines:
            append_lines.append(fa)
            append_lines.append(sab)
        #elif fc in source_lines and fd not in source_lines:
        #    append_lines.append(fd)
        #    append_lines.append(sdc)
        #elif fc not in source_lines and fd in source_lines:
        #    append_lines.append(fc)
        #    append_lines.append(scd)
        else:
            append_lines.append(fa)
            append_lines.append(fb)
            append_lines.append(sab)

    #     for i in range(len(sub_funcs)):
    #         current_func = ".globl {0}\n".format(sub_funcs[i])
    #         if current_func in not in
    #         if ".globl {0}\n".format(sub_funcs[i]) not in append_dict:
    #             # 1,只走着一步
    #             append_dict[".globl {0}\n".format(sub_funcs[i])] = [".globl {0}\n".format(sub_funcs[i])]
    #         if i > 0:
    #             # 非1，还要走这一步
    #             append_dict[".globl {0}\n".format(sub_funcs[i])].append(
    #                 ".set {0},{1}\n".format(sub_funcs[i], sub_funcs[0]))
    # source_lines = []
    # with open(source_file, "r") as f:
    #     source_lines = f.readlines()
    # for gl, aplines in append_dict.items():
    #     if gl in source_lines:
    #         continue
    #     else:
    #         append_lines += aplines
    source_lines = section_reset(source_lines, start_flags=[".section", ".init_array"], end_flags=[".section"])

    source_lines += append_lines
    with open(save_file, "w") as f:
        f.writelines(source_lines)
    return


def load_analysis_cache(loader, outfile):
    with open(outfile + ".analysis_cache") as fd:
        analysis = json.load(fd)
    print("[*] Loading analysis cache")
    for func, info in analysis.items():
        for key, finfo in info.items():
            loader.container.functions[int(func)].analysis[key] = dict()
            for k, v in finfo.items():
                try:
                    addr = int(k)
                except ValueError:
                    addr = k
                loader.container.functions[int(func)].analysis[key][addr] = v


def save_analysis_cache(loader, outfile):
    analysis = dict()

    for addr, func in loader.container.functions.items():
        analysis[addr] = dict()
        analysis[addr]["free_registers"] = dict()
        for k, info in func.analysis["free_registers"].items():
            analysis[addr]["free_registers"][k] = list(info)

    with open(outfile + ".analysis_cache", "w") as fd:
        json.dump(analysis, fd)


def analyze_registers(loader, args):
    StackFrameAnalysis.analyze(loader.container)
    if args.cache:
        try:
            load_analysis_cache(loader, args.outfile)
        except IOError:
            RegisterAnalysis.analyze(loader.container)
            save_analysis_cache(loader, args.outfile)
    else:
        RegisterAnalysis.analyze(loader.container)


def asan(rw, loader, args):
    analyze_registers(loader, args)

    instrumenter = Instrument(rw)
    instrumenter.do_instrument()
    instrumenter.dump_stats()


def readfile(fileread):
    fo = open("fileread", "r")
    for line in fo.readlines():
        if line.strip() == '':
            continue
        line = line.strip()  # 去掉每行头尾空白
        print("%s" % (line))
        fo.close()


def asank(rw, loader, args):
    StackFrameAnalysis.analyze(loader.container)

    with tempfile.NamedTemporaryFile(mode='w') as cf_file:
        with tempfile.NamedTemporaryFile(mode='r') as regs_file:
            rw.dump_cf_info(cf_file)
            cf_file.flush()

            subprocess.check_call(['cftool', cf_file.name, regs_file.name])

            analysis = json.load(regs_file)

            for func, info in analysis.items():
                for key, finfo in info.items():
                    fn = loader.container.get_function_by_name(func)
                    fn.analysis[key] = dict()
                    for k, v in finfo.items():
                        try:
                            addr = int(k)
                        except ValueError:
                            addr = k
                        fn.analysis[key][addr] = v

    return rw


if __name__ == "__main__":
    if  os.path.exists("bss_instruction_addr.txt"):
        os.remove("bss_instruction_addr.txt")
    print("Firster position")
    argp = argparse.ArgumentParser(description='Process some integers.')

    argp.add_argument("bin", type=str, help="Input binary to load")
    argp.add_argument("outfile", type=str, help="Symbolized ASM output")

    argp.add_argument("-a", "--asan", action='store_true',
                      help="Add binary address sanitizer instrumentation")
    # python3 -m rwtools.asan.asantool /bin/ls ls-basan-instrumented
    print("position 1")
    argp.add_argument("-m", "--module", type=str,
                      help="Use specified instrumentation module in rwtools directory")
    print("position 2")

    # argp.add_argument("-s", "--assembly", action="store_true",
    # help="Generate Symbolized Assembly")
    # python3 -m librw.rw </path/to/binary> <path/to/output/asm/files>
    argp.add_argument("-k", "--kernel", action='store_true',
                      help="Instrument a kernel module")
    print("position 3")
    argp.add_argument(
        "--kcov", action='store_true', help="Instrument the kernel module with kcov")
    print("position 4")
    argp.add_argument("-c", "--cache", action='store_true',
                      help="Save/load register analysis cache (only used with --asan)")
    argp.add_argument("--ignore-no-pie", dest="ignore_no_pie", action='store_true',
                      help="Ignore position-independent-executable check (use with caution)")
    argp.add_argument("--ignore-stripped", dest="ignore_stripped", action='store_true',
                      help="Ignore stripped executable check (use with caution)")
    argp.add_argument("-v", "--verbose", action="store_true",
                      help="Verbose output")
    print("position 5")
    argp.set_defaults(ignore_no_pie=False)
    argp.set_defaults(ignore_stripped=False)
    print('argp = ', type(argp))
    print(argp)
    args = argp.parse_args()
    print(args, "start")
    rwtools_path = "rwtools."
    print("position 6")
    table_path = gen_table_file(args.bin)
    same_functions = gen_same_functions(table_path, 2, 3)
    # source args.bin root/quickfuzz-zhenming/libtest/libstagefright.so
    # out /root/quickfuzz-zhenming/libtest/libstagefright.s
    from elftools.elf.elffile import ELFFile

    elffile = ELFFile(open(args.bin, "rb"))
    print("This is jump")
    arch = elffile.get_machine_arch()
    print("This is jump2")
    print(arch)
    if arch == "AArch64":
        print("This is jump3")
        from arm.librw.rw import Rewriter

        print("This is jump4")
        from arm.librw.analysis.register import RegisterAnalysis

        print("This is jump5")
        from arm.librw.analysis.stackframe import StackFrameAnalysis
        from arm.rwtools.asan.instrument import Instrument
        from arm.librw.loader import Loader
        from arm.librw.analysis import register
        import arm.librw.util.logging

        print("position AArch64")
        rwtools_path = "arm." + rwtools_path
        print(rwtools_path)

        if args.verbose:
            arm.librw.util.logging.DEBUG_LOG = True

    elif arch == "x64":
        if args.kernel:
            from librw.krw import Rewriter
            from librw import krw
            from librw.analysis.kregister import RegisterAnalysis
            from librw.analysis.kstackframe import StackFrameAnalysis
            from librw.kloader import Loader
            from librw.analysis import kregister
        else:
            from rw import Rewriter
            from librw.analysis.register import RegisterAnalysis
            from librw.analysis.stackframe import StackFrameAnalysis
            from rwtools.asan.instrument import Instrument
            from librw.loader import Loader
            from librw.analysis import register
    else:
        print(f"Architecture {arch} not supported!")
        exit(1)

    loader = Loader(args.bin)
    print(loader)
    print("position 7")
    if loader.is_pie() == False and args.ignore_no_pie == False:
        print("***** RetroWrite requires a position-independent executable. *****")
        print("It looks like %s is not position independent" % args.bin)
        print("position 4")
        print("If you really want to continue, because you think retrowrite has made a mistake, pass --ignore-no-pie.")
        sys.exit(1)
    if loader.is_stripped() == True and args.ignore_stripped == False:
        print("position 8")
        print("quickfuzz requires a non-stripped executable.")
        print("It looks like %s is stripped" % args.bin)
        print(
            "If you really want to continue, because you think retrowrite has made a mistake, pass --ignore-stripped.")
        sys.exit(1)

    flist = loader.flist_from_symtab()
    with open("flist.txt", "w") as f:
        json.dump(flist, f)
    flist = SizeTrans().func_adjust(flist)
    # with open("flist.txt","w") as f:
    #    json.dump(flist, f)
    loader.load_functions(flist)
    # with open("symbol_tables.txt", 'w'):
    #       json.dump(symbol_tables)

    slist = loader.slist_from_symtab()
    if args.kernel:
        loader.load_data_sections(slist, krw.is_data_section)
    else:
        loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)

    #reloc_list = loader.reloc_list_from_symtab()
    reloc_list = loader.reloc_list_from_llvm_readelf()
    # print(reloc_list)
    loader.load_relocations(reloc_list)

    global_list = loader.global_data_list_from_symtab()
    # print(global_list)
    loader.load_globals_from_glist(global_list)

    loader.container.attach_loader(loader)
    print("position 9")
    print(loader.container)
    print(args.outfile)
    rw = Rewriter(loader.container, args.outfile)
    rw.symbolize()
    print(args, "end")
    if args.asan:
        print("This  is  asan")
        if args.kernel:
            rewriter = asank(rw, loader, args)
            instrumenter = Instrument(rewriter)
            instrumenter.do_instrument()

            if args.kcov:
                kcov_instrumenter = KcovInstrument(rewriter)
                kcov_instrumenter.do_instrument()
            rewriter.dump()
        else:
            asan(rw, loader, args)
            rw.dump()
    elif args.module:
        print("This  is  asanelseif", args.module)
        try:
            module = importlib.import_module(rwtools_path + args.module + ".instrument")
            instrument = getattr(module, "Instrument")

            analyze_registers(loader, args)
            instrumenter = instrument(rw)
            instrumenter.do_instrument()
            rw.dump()
        except Exception as e:
            print("Exception as blow", e)
            traceback.print_exc()
    else:
        rw.dump()
        print("This  is  asanelse")

    append_function_to_result_2(same_functions, args.outfile)


