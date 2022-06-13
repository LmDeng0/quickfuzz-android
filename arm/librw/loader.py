#!/usr/bin/env python

import argparse
from collections import defaultdict

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.relocation import RelocationSection

from .container import Container, Function, DataSection
from .disasm import disasm_bytes
import json 
from arm.librw.util.logging import *

import os
import string
import random
import re
import struct
from collections import defaultdict
from elftools.elf.enums import ENUM_RELOC_TYPE_AARCH64



class Loader():
    def __init__(self, fname):
        debug(f"Loading {fname}...")
        self.fname = fname
        self.fd = open(fname, 'rb')
        self.elffile = ELFFile(self.fd)
        self.container = Container()
        print(self.elffile['e_type'])

    def is_stripped(self):
        # Get the symbol table entry for the respective symbol
        symtab = self.elffile.get_section_by_name('.symtab')
        if not symtab:
            print('No symbol table available, this file is probably stripped!')
            return True

        sym = symtab.get_symbol_by_name("main")
        if not sym:
            print('Symbol {} not found')
            return True
        return False

    def is_pie(self):
        base_address = next(seg for seg in self.elffile.iter_segments() 
                if seg['p_type'] == "PT_LOAD")['p_vaddr']
        return self.elffile['e_type'] == 'ET_DYN' and base_address == 0

    def load_functions(self, fnlist):
        debug(f"Loading functions...")
        section = self.elffile.get_section_by_name(".text")
        data = section.data()
        base = section['sh_addr']
        size = section['sh_size']
        if not self.is_stripped():
            for faddr, fvalue in fnlist.items():
                section_offset = faddr - base
                bytes = data[section_offset:section_offset + fvalue["sz"]]

                fixed_name = fvalue["name"].replace("@", "_")
                bind = fvalue["bind"] if fixed_name != "main" else "STB_GLOBAL" #main should always be global
                function = Function(fixed_name, faddr, fvalue["sz"], bytes, bind)
                self.container.add_function(function)
        else:
            sorted_func_addrs = sorted(fnlist.keys())
            assert len(sorted_func_addrs) > 0, "There is no functions!"
            fns_length = len(sorted_func_addrs)
            if sorted_func_addrs[0] > base:
                fixed_name = f"func_{hex(base)}"
                section_offset = 0
                sz = sorted_func_addrs[0] - base
                bytes = data[section_offset:section_offset + sz]
                bind = "STB_GLOBAL"
                function = Function(fixed_name, base, sz, bytes, bind)
                self.container.add_function(function)

            for i, addr in enumerate(sorted_func_addrs):
                section_offset = addr - base
                fvalue = fnlist[addr]
                if i < fns_length - 1:
                    next_addr = sorted_func_addrs[i + 1]
                else:
                    next_addr = base + size
                sz = next_addr - addr if (next_addr - addr) > fvalue["sz"] else fvalue["sz"]
                fixed_name = fvalue["name"].replace("@", "_")
                bytes = data[section_offset:section_offset + sz]
                bind = fvalue["bind"] if fixed_name != "main" else "STB_GLOBAL" #main should always be global
                function = Function(fixed_name, addr, sz, bytes, bind)
                self.container.add_function(function)

    def load_data_sections(self, seclist, section_filter=lambda x: True):
        debug(f"Loading sections...")
        for sec in [sec for sec in seclist if section_filter(sec)]:
            sval = seclist[sec]
            section = self.elffile.get_section_by_name(sec)
            data = section.data()
            more = bytearray()
            if sec == ".init_array":
                if len(data) > 8:
                    data = data[8:]
                else:
                    data = b''
                more.extend(data)
            else:
                more.extend(data)
                if len(more) < sval['sz']:
                    more.extend(
                        [0x0 for _ in range(0, sval['sz'] - len(more))])

            bytes = more
            print(sec, hex(sval["base"]))
            ds = DataSection(sec, sval["base"], sval["sz"], bytes,
                             (sval['align']))

            self.container.add_section(ds)

        # Find if there is a plt section
        for sec in seclist:
            if sec == '.plt':
                self.container.plt_base = seclist[sec]['base']
            if sec == ".plt.got":
                section = self.elffile.get_section_by_name(sec)
                data = section.data()
                entries = list(
                    disasm_bytes(section.data(), seclist[sec]['base']))
                self.container.gotplt_base = seclist[sec]['base']
                self.container.gotplt_sz = seclist[sec]['sz']
                self.container.gotplt_entries = entries

    def load_relocations(self, relocs):
        for reloc_section, relocations in relocs.items():

            # transform stuff like ".rela.dyn" in ".dyn"
            section = reloc_section[5:]

            if reloc_section == ".rela.plt":
                self.container.add_plt_information(relocations)

            if section in self.container.sections:
                self.container.sections[section].add_relocations(relocations)
            else:
                print("[*] Relocations for a section that's not loaded:",
                      reloc_section)
                self.container.add_relocations(section, relocations)

    def reloc_list_from_llvm_readelf(self):
        file = self.fname

        load_ranges = list()
        t_file = open(file, "rb")
        content = t_file.read()
        # t_file.close()
        sec_infos = list()

        def _is_in_load_ranges(addr):
            for (start, end) in load_ranges:
                if addr >= start and addr < end:
                    return True
            return False

        def _retrive_sec_info(addr):
            for (start, size, s_offset) in sec_infos:
                if addr >= start and addr < size + start:
                    return addr - start + s_offset
            return -1

        elffile = ELFFile(t_file)
        for seg in elffile.iter_segments():
            if seg['p_type'] != 'PT_LOAD':
                continue

            load_ranges.append((seg['p_vaddr'], seg['p_vaddr'] + seg['p_memsz']))
        
        for sec in elffile.iter_sections():
            sec_name = sec.name
            if sec_name == "":
                continue
            sec_start = sec['sh_addr']
            sec_offset = sec['sh_offset']
            sec_infos.append((sec_start, sec['sh_size'], sec_offset))

        error_msg = "Please specify the path of llvm-readelf and make sure the version >= 11.0.0. export LLVM_READELF=/path/to/llvm-readelf"
        def randomString(stringLength = 10):
            letters = string.ascii_lowercase
            return ''.join(random.choice(letters) for i in range(stringLength))

        def execute_output(cmd):
            tmp_out = randomString()
            os.system("%s > /tmp/%s" % (cmd, tmp_out))
            with open("/tmp/%s" % tmp_out, 'r+') as tmp_f:
                out = tmp_f.read().strip()

            os.system('rm /tmp/%s' % tmp_out)
            return out

        def get_absoluste_llvm_path(path):
            out = execute_output("which %s" % path)
            return out

        def get_llvm_path():
            readelf = os.getenv('LLVM_READELF')
            if readelf is None:
                readelf = "llvm-readelf"
            readelf_path = get_absoluste_llvm_path(readelf)
            if os.path.exists(readelf_path):
                return readelf_path
            return None

        def _check_version(path):
            out = execute_output("%s --version" % path)
            for line in out.split("\n"):
                if "LLVM version" in line:
                    version = line.strip().split(" ")[-1]
                    main_version = int(version.split('.')[0])
                    if main_version < 11:
                        print(error_msg)
                        exit(-1)

        llvm_path = get_llvm_path()
        if llvm_path is None or not os.path.exists(llvm_path):
            print(error_msg)
            exit(-1)
        _check_version(llvm_path)

        # read relocations from llvm-readelf
        tmp_output = randomString()
        os.system("%s -r %s > /tmp/%s" % (llvm_path, file, tmp_output))
        relocs = defaultdict(list)
        secname = ""
        with open("/tmp/%s" % tmp_output, 'r+') as relocFile:
            for line in relocFile:
                if len(line.strip()) == 0:
                    continue

                if 'Relocation section' in line:
                    secname = line.split(' ')[2]
                    secname = secname.split('\'')[1]
                    print(secname)
                    continue
                entry = re.split('\s+', line.strip())
                if len(entry) != 7 and len(entry) != 3:
                    print("skip entry %s" % line)
                    continue

                symbol_name = None
                st_value = None
                addend = 0
                try:
                    offset = int(entry[0], 16)
                except:
                    continue
                e_type = ENUM_RELOC_TYPE_AARCH64[entry[2]]
                type_name = entry[2]
                if len(entry) > 3:
                    st_value = int(entry[3], 16)
                    symbol_name = entry[4]
                    symbol_name = symbol_name.replace("@LIBLOG", "")
                    symbol_name = symbol_name.replace("@LIBC_OMR1", "")
                    symbol_name = symbol_name.replace("@LIBC", "")
                    addend = int(entry[6])
                elif secname == ".relr.dyn" and type_name == "R_AARCH64_RELATIVE" and _is_in_load_ranges(offset):
                    f_offset = _retrive_sec_info(offset)
                    bytes = content[f_offset: f_offset+8]
                    pointer = struct.unpack("<Q", bytes)[0]
                    if _is_in_load_ranges(pointer):
                        addend = pointer

                    

                
                # if symbol_name == None:
                #     continue

                reloc_i = {
                    'name': symbol_name,
                    'st_value': st_value,
                    'offset': offset,
                    'addend': addend,
                    'type': e_type,
                }

                relocs[secname].append(reloc_i)
        os.system("rm /tmp/%s" % tmp_output)
        return relocs

    def reloc_list_from_symtab(self):
        relocs = defaultdict(list)

        for section in self.elffile.iter_sections():
            if not isinstance(section, RelocationSection):
                continue

            symtable = self.elffile.get_section(section['sh_link'])

            for rel in section.iter_relocations():
                symbol = None
                if rel['r_info_sym'] != 0:
                    symbol = symtable.get_symbol(rel['r_info_sym'])

                if symbol:
                    if symbol['st_name'] == 0:
                        symsec = self.elffile.get_section(symbol['st_shndx'])
                        symbol_name = symsec.name
                    else:
                        symbol_name = symbol.name
                else:
                    symbol = dict(st_value=None)
                    symbol_name = None

                reloc_i = {
                    'name': symbol_name,
                    'st_value': symbol['st_value'],
                    'offset': rel['r_offset'],
                    'addend': rel['r_addend'],
                    'type': rel['r_info_type'],
                }

                relocs[section.name].append(reloc_i)

        return relocs
        

    def flist_from_symtab(self):
        symbol_tables = [
            sec for sec in self.elffile.iter_sections()
            if isinstance(sec, SymbolTableSection)
        ]

        function_list = dict()
        #symobl_sections = []
        for section in symbol_tables:
            if not isinstance(section, SymbolTableSection):
                continue

            if section['sh_entsize'] == 0:
                continue

            for symbol in section.iter_symbols():
                if symbol['st_other']['visibility'] == "STV_HIDDEN":
                    continue
                #symobl_sections.append(symbol)
                if (symbol['st_info']['type'] == 'STT_FUNC'
                        and symbol['st_shndx'] != 'SHN_UNDEF'):
                    function_list[symbol['st_value']] = {
                        'name': symbol.name,
                        'sz': symbol['st_size'],
                        'visibility': symbol['st_other']['visibility'],
                        'bind': symbol['st_info']['bind'],
                    }
        #with open("symbol_sections.txt", "w") as f:
        #    json.dump(symobl_sections, f)

        ##  首先对所有的function函数进行排序；
        ##  如果函数的首地址加上他的size大于下一个函数的首地址
        ##  把下一个函数的首地址扩大，扩大成上一个函数的首地址加上他的size
        ##  修改size


        ##  现在对整个flist进行人为排序
        ##  是否需要处理完之后，恢复原来的顺序

        ##  Plan B
        ##  函数A的地址加上函数A的size，函数B的Size，如果函数A的地址加上函数A的size大于函数B的首地址，修改函数A的size
        ##  函数A的size，应该是函数B的首地址减去函数A的首地址
        return function_list

    def slist_from_symtab(self):
        sections = dict()
        for section in self.elffile.iter_sections():
            sections[section.name] = {
                'base': section['sh_addr'],
                'sz': section['sh_size'],
                'offset': section['sh_offset'],
                'align': section['sh_addralign'],
            }

        return sections

    def load_globals_from_glist(self, glist):
        self.container.add_globals(glist)

    def global_data_list_from_symtab(self):
        symbol_tables = [
            sec for sec in self.elffile.iter_sections()
            if isinstance(sec, SymbolTableSection)
        ]

        global_list = defaultdict(list)

        for section in symbol_tables:
            if not isinstance(section, SymbolTableSection):
                continue

            if section['sh_entsize'] == 0:
                continue

            for symbol in section.iter_symbols():
                # XXX: HACK
                if "@@GLIBC" in symbol.name:
                    continue
                if symbol['st_other']['visibility'] == "STV_HIDDEN":
                    continue
                if symbol['st_size'] == 0:
                    continue

                if (symbol['st_info']['type'] == 'STT_OBJECT'
                        and symbol['st_shndx'] != 'SHN_UNDEF'):
                    global_list[symbol['st_value']].append({
                        'name':
                        "{}_{:x}".format(symbol.name, symbol['st_value']),
                        'sz':
                        symbol['st_size'],
                    })

        return global_list


if __name__ == "__main__":
    from .rw import Rewriter

    argp = argparse.ArgumentParser()

    argp.add_argument("bin", type=str, help="Input binary to load")
    argp.add_argument(
        "--flist", type=str, help="Load function list from .json file")

    args = argp.parse_args()

    loader = Loader(args.bin)

    flist = loader.flist_from_symtab()
    loader.load_functions(flist)

    slist = loader.slist_from_symtab()
    loader.load_data_sections(slist, lambda x: x in Rewriter.DATASECTIONS)

    reloc_list = loader.reloc_list_from_symtab()
    loader.load_relocations(reloc_list)

    global_list = loader.global_data_list_from_symtab()
    loader.load_globals_from_glist(global_list)
