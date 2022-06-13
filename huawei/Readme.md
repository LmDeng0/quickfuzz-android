## Usage

**Please specify the path of llvm-readelf and make sure the version >= 11.0.0. export LLVM_READELF=/path/to/llvm-readelf**

export LLVM_READELF="/data/llvm-11.0.0.src/build/bin/llvm-readelf"

quickfuzz -m asan --ignore-stripped libaudioprocessing.so libaudioprocessing.s

**注释以下内容**
*****************************************************************************
**.globl __cfi_check
.type __cfi_check, @function
__cfi_check:
.LC155d8:
	ret 
.size __cfi_check,.-__cfi_check**

.globl _ZN7android21RecordBufferConverterC1Ej14audio_format_tjjS1_j
.set _ZN7android21RecordBufferConverterC1Ej14audio_format_tjjS1_j,_ZN7android21RecordBufferConverterC2Ej14audio_format_tjjS1_j
.globl _ZN7android24ClampFloatBufferProviderC2Eim

.globl _ZN7android17AudioResamplerDynIssiEC1EiiNS_14AudioResampler11src_qualityE
.globl _ZN7android17AudioResamplerDynIssiEC2EiiNS_14AudioResampler11src_qualityE
.set _ZN7android17AudioResamplerDynIssiEC1EiiNS_14AudioResampler11src_qualityE,_ZN7android17AudioResamplerDynIssiEC2EiiNS_14AudioResampler11src_qualityE


.globl _ZN7android17AudioResamplerDynIisiEC1EiiNS_14AudioResampler11src_qualityE
.globl _ZN7android17AudioResamplerDynIisiEC2EiiNS_14AudioResampler11src_qualityE
.set _ZN7android17AudioResamplerDynIisiEC1EiiNS_14AudioResampler11src_qualityE,_ZN7android17AudioResamplerDynIisiEC2EiiNS_14AudioResampler11src_qualityE

.globl _ZN7android17AudioResamplerDynIfffEC1EiiNS_14AudioResampler11src_qualityE
.globl _ZN7android17AudioResamplerDynIfffEC2EiiNS_14AudioResampler11src_qualityE
.set _ZN7android17AudioResamplerDynIfffEC1EiiNS_14AudioResampler11src_qualityE,_ZN7android17AudioResamplerDynIfffEC2EiiNS_14AudioResampler11src_qualityE


*****************************************************************
### 如果更跟文件名，请在相应的./quickfuzz_script/convert_main.py和GOTRebuild.py中修改

python convert_main.py

python GOTRebuild.py

