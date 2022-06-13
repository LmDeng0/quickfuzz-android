## Usage

**Please specify the path of llvm-readelf and make sure the version >= 11.0.0. export LLVM_READELF=/path/to/llvm-readelf**
export LLVM_READELF="/data/llvm-11.0.0.src/build/bin/llvm-readelf"

quickfuzz -m asan --ignore-stripped libaudioprocessing.so libaudioprocessing.s

