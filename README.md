# Task List
## X86/ARM 
（a）Address Sanitizer；（b）AFL；逸博 10/11
## Documentation
- 黎明 10/11  
 (a) 安装 Install  
 (b) 部署 Deploy  
 (c) 用例 Cases  
 (d) 测评 Evaluation：（1）代码扩大多少倍;（2）运行速度; 5.1 Retrowrite  time: 5.2  
## Docker容器化
（ARM，X86）逸博 10/11
## Techniques：
 Retrowrite：Instrumentation；Code Coverage；Address Sanitizer；黎明 10/11


# Pitfalls
## Unable to request new process from fork server
```
(quickfuzz-aarch64) root@quickfuzz:~/quickfuzz/demos/fuzzgoat# /root/quickfuzz/third-party/afl/afl-fuzz -i in -o out ./fuzzgoat.afl @@
afl-fuzz 2.52b by <lcamtuf@google.com>
[+] You have 8 CPU cores and 3 runnable tasks (utilization: 38%).
[+] Try parallel jobs - see /usr/local/share/doc/afl/parallel_fuzzing.txt.
[*] Checking CPU core loadout...
[+] Found a free CPU core, binding to #0.
[*] Checking core_pattern...
[*] Setting up output directories...
[+] Output directory exists but deemed OK to reuse.
[*] Deleting old session data...
[+] Output dir cleanup successful.
[*] Scanning 'in'...
[+] No auto-generated dictionary tokens to reuse.
[*] Creating hard links for all input files...
[*] Validating target binary...
[*] Attempting dry run with 'id:000000,orig:seed'...
[*] Spinning up the fork server...
[+] All right - fork server is up.

[-] PROGRAM ABORT : Unable to request new process from fork server (OOM?)
         Location : run_target(), afl-fuzz.c:2377

(quickfuzz-aarch64) root@quickfuzz:~/quickfuzz/demos/fuzzgoat# dmesg
[ 2345.681538] Unsafe core_pattern used with fs.suid_dumpable=2.
               Pipe handler or fully qualified core dump path required.
               Set kernel.core_pattern before fs.suid_dumpable.

```

# quickfuzz


The two versions can be used independently of each other or at the same time.
In case you want to use both please follow the instructions for KRetrowrite.

## General setup

Retrowrite is implemented in python3 (3.6). Make sure python3 and python3-venv
is installed on system. Retrowrite depends on
[capstone](https://github.com/aquynh/capstone). The version
available from the Ubuntu 18.04 repositories 
is not compatible with this version. The setup
script pulls the latest version of capstone from the repository and builds it.
Make sure that your system meets the requirements to build capstone.

#### Requirements for target binary

The target binary
* must be compiled as position independent code (PIC/PIE)
* must be x86_64 (32 bit at your own risk)
* must contain symbols (i.e., not stripped; if stripped, please recover
  symbols first)
* must not contain C++ exceptions (i.e., C++ exception tables are not
  recovered and simply stripped during lifting)

#### Command line helper

The individual tools also have command line help which describes all the
options, and may be accessed with `-h`. 
To start with use retrowrite command:

```bash
(retro) $ quickfuzz --help
usage: quickfuzz [-h] [-a] [-s] [-k] [--kcov] [-c] [--ignore-no-pie] [--ignore-stripped] bin outfile

Retrofitting compiler passes though binary rewriting.

positional arguments:
  bin                Input binary to load
  outfile            Symbolized ASM output

optional arguments:
  -h, --help         show this help message and exit
  -a, --asan         Add binary address sanitizer instrumentation
  -s, --assembly     Generate Symbolized Assembly
  -k, --kernel       Instrument a kernel module
  --kcov             Instrument the kernel module with kcov
  -c, --cache        Save/load register analysis cache (only used with --asan)
  --ignore-no-pie    Ignore position-independent-executable check (use with caution)
  --ignore-stripped  Ignore stripped executable check (use with caution)
```

In case you load a non position independent code you will get the following message:
```
(quickfuzz) $ quickfuzz stack stack.c 
***** quickfuzz requires a position-independent executable. *****
It looks like stack is not position independent
If you really want to continue, because you think retrowrite has made a mistake, pass --ignore-no-pie.
```
In the case you think retrowrite is mistaking you can use the argument `--ignore-no-pie`.


## quickfuzz
### Quick Usage Guide

This section highlights the steps to get you up to speed to use userspace quickfuzz for rewriting PIC binaries.

quickfuzz ships with an utility with the following features:
* Generate symbolized assembly files from binaries without source code
* BASan: Instrument binary with binary-only Address Sanitizer 
* Support for symbolizing (linux) kernel modules 
* KCovariance instrumentation support

### Setup

Run `setup.sh`:

* `./setup.sh user`

Activate the virtualenv (from root of the repository):

* `source retro/bin/activate`

(Bonus) To exit virtualenv when you're done with retrowrite:
* `deactivate`


### Usage

#### Commands




##### a. Instrument Binary with Binary-Address Sanitizer (BASan)

`rquickfuzz --asan </path/to/binary/> </path/to/output/binary>`

Note: Make sure that the binary is position-independent and is not stripped.
This can be checked using `file` command (the output should say `ELF shared object`).

Example, create an instrumented version of `/bin/ls`:

`quickfuzz --asan /bin/ls ls-basan-instrumented`

This will generate an assembly (`.s`) file that can be assembled and linked
using any compiler, example:

`gcc ls-basan-instrumented.s -lasan -o ls-basan-instrumented`

**debug** in case you get the error ```undefined reference to `__asan_init_v4'``` , 
replace "asan_init_v4" by "asan_init"  in the assembly file, the following command can help you do that:
```sed -i 's/asan_init_v4/asan_init/g' ls-basan-instrumented.s```

##### b. Generate Symbolized Assembly

To generate symbolized assembly that may be modified by hand or post-processed
by existing tools:

`quickfuzz </path/to/binary> <path/to/output/asm/files>`

Post-modification, the asm files may be assembled to working binaries as
described above.

While retrowrite is interoperable with other tools, we
strongly encourage researchers to use the retrowrite API for their binary
instrumentation / modification needs! This saves the additional effort of
having to load and parse binaries or assembly files. Check the developer
sections for more details on getting started.


##### c. Instrument Binary with AFL

To generate an AFL instrumented binary, first generate the symbolized assembly
as described above. Then, recompile the symbolized assembly with `afl-gcc` from
[afl++](https://github.com/vanhauser-thc/AFLplusplus) like this:

```
$ AFL_AS_FORCE_INSTRUMENT=1 afl-gcc foo.s -o foo
```
 or `afl-clang`.


## Docker / Reproducing Results

See [fuzzing/docker](fuzzing/docker) for more information on building a docker image for
fuzzing and reproducing results.



# KRetrowrite
### Quick Usage Guide
### Setup

Run `setup.sh`:

* `./setup.sh kernel`


Activate the virtualenv (from root of the repository):

* `source retro/bin/activate`

(Bonus) To exit virtualenv when you're done with retrowrite:
* `deactivate`


### Usage


#### Commands

##### Classic instrumentation

* Instrument Binary with Binary-Address Sanitizer (BASan)  :`retrowrite --asan --kernel </path/to/module.ko> </path/to/output/module_asan.ko>`
* Generate Symbolized Assembly that may be modified by hand or post-processed by existing tools: `retrowrite </path/to/module.ko> <path/to/output/asm/files>`

##### Fuzzing

For fuzzing campaign please see [fuzzing/](fuzzing/) folder.

# Developer Guide

In general, `librw/` contains the code for loading, disassembly, and
symbolization of binaries and forms the core of all transformations.
Individual transformation passes that build on top this rewriting framework,
such as our binary-only Address Sanitizer (BASan) is contained as individual
tools in `rwtools/`.

The files and folder starting with `k` are linked with the kernel retrowrite version.

# Demos

In the [demos/](demos/) folder, you will find examples for userspace and kernel retrowrite
([demos/user_demo](demos/user_demo) and [demos/kernel_demo](demos/kernel_demo) respectively).




