# 用脚本从 idaJmpTbl.py 获取 jumptable 的信息， 将生成的 JumpTable 文件存入 
# quickfuzz 的路径下/root/quickfuzz-liming2/arm/librw/rw.py 目录下，并替换/rw.py 218 行的文件名；

### 具体操作流程： 用 ida64位打开 libaudioprocessing.o.so 库文件， 点击 file→Script file…，
### 然后选择 idaJump.py 脚本读入，会在对应目录下生成 JumpTable 文件。


## bss 段修改
# 用 convert_main.py 脚本修改.bss 段的信息，在 quickfuzz 处理过程中有/root/quickfuzz-liming2/bbs_func.txt 文件生成，将 bss_func.txt 放入 covert_main.py 的同一目录下，运行脚本生成 libaudioprocessing_asan_bss.s 文件；

### 注意，执行脚本时需要修改脚本的输入输出的文件信息（convert_main.py \#143\#147）

## got 段修改段修改
用生成的 GOTRebuild.py 脚本修改 GOT 表信息，将 JumpTable 和 libaudioproces
sing_asan_bss.s 作为输入，生成 libaudioprocessing_asan_bss_got.s 文件；

### 注意，执行脚本时需要修改脚本的输入输出的文件信息（GOTRebuild.py \#5\#6\#9）

## tbnz 跳转距离过长修改
在.s 编译到.o 阶段生成的错误保存为 error.txt，修改跳转距离过长的问题，使用
脚本 Tbnz_main.py， 以 error.txt 和 libaudioprocessing_asan_bss_got.s 作为输入，生成 libaudioprocessing_asan_bss_got_tbnz.s 文件。


###### 注意，quickfuzz生成的.s_asan.s才是最后的.s文件（删除原来的.s，把.s_asan.s替换成.s，这里不管加没加asan）
## .s -> _bss.s -> _bss_got.s -> _bss_got_tbnz.s
