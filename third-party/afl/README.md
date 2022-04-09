https://github.com/mirrorer/afl.git

重写了afl-as.c/afl-as.h，使得其能在arm平台下进行插桩。

- 编译:
```
export AFL_NO_X86=1
make && make install
```

- 使用：

```
export AFL_USE_ARM=1
afl-gcc xxx // 用afl-gcc进行编译
```
