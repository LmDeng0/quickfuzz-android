# ARM漏洞挖掘

## （a）Install

### quickfuzz setup

```shell
git clone https://github.com/leonidwang/quickfuzz.git
```

Run `setup.sh`:

```shell
bash ./setup.sh users
```

Activate the virtualenv (from root of the repository):

In X86 env
```shell
source ./quickfuzz-x86_64/bin/activate
```

In ARM env
```shell
source ./quickfuzz-aarch64/bin/activate
```
(Bonus) To exit virtualenv when you're done with retrowrite:

```shell
deactivate
```




## （b）Deploy

先进行asan插桩，再进行AFL插桩

### quickfuzz 插桩 asan

```shell
quickfuzz -a  test.so test_asan.s

sed -i 's/__asan_init_v4/__asan_init/g' test_asan.s

g++ -shared -fPIC test_asan.s -lasan  -o test_asan.so
```



### quickfuzz 插桩 afl

```shell
quickfuzz test_asan.so test_asan_afl.s

sed -i 's/__cxa_finalize//g' test_asan_afl.s

cp destination.s /tmp

AFL_AS_FORCE_INSTRUMENT=1 afl-g++ -fPIC -pie -shared /tmp/test_asan_afl.s -o test_asan_afl.so
```

### Docker


## （c）Cases
### 用uaf作为测试样例，插桩asan
```shell
gcc -g uaf.c -o uaf

quickfuzz -a uaf uaf-asan.s

sed -i 's/__asan_init_v4/__asan_init/g' uaf-asan.s

gcc uaf-asan.s -lasan  -o uaf-asan

./uaf-asan
```
### 用heapoverflow作为测试样例，插桩asan
```shell
gcc -g heapoverflow.c -o heapoverflow

quickfuzz -a uaf heapoverflow-asan.s

sed -i 's/__asan_init_v4/__asan_init/g' heapoverflow-asan.s

gcc heapoverflow-asan.s -lasan  -o heapoverflow-asan

./heapoverflow-asan
```
### 用uaf作为测试样例，插桩afl
```shell
gcc -g uaf.c -o uaf

quickfuzz uaf uaf-afl.s

sed -i 's/__cxa_finalize//g' uaf-afl.s (optional)

export AFL_USE_ARM=1

AFL_AS_FORCE_INSTRUMENT=1 afl-gcc  uaf-afl.s -o uaf-afl
```
### 用heapoverflow作为测试样例，插桩afl
```shell
gcc -g heapoverflow.c -o heapoverflow

quickfuzz heapoverflow heapoverflow.s

sed -i 's/__cxa_finalize//g' heapoverflow.s (optional)

export AFL_USE_ARM=1

AFL_AS_FORCE_INSTRUMENT=1 afl-gcc  heapoverflow-afl.s -o heapoverflow-afl
```
## （d）Evaluation

### 1）代码量扩大

### 2）运行速度

