from pathlib import Path
import ctypes,ctypes.util,json
root=Path(__file__).resolve().parent.parent;folder=root/'gpu_kernel';lib=folder/'lib'
original=Path('__SERVER_USER_ROOT__/projects/BlenderWorld/runtime/blender-4.2.10-linux-x64/4.2/scripts/addons_core/cycles')
for source in original.iterdir():
 if source.name=='lib':continue
 target=folder/source.name
 if not target.exists():target.symlink_to(source,target_is_directory=source.is_dir())
for source in (original/'lib').iterdir():
 target=lib/source.name
 if not target.exists():target.symlink_to(source)
p=lib/'kernel_sm_80.cubin';data=p.read_bytes();zstd=ctypes.CDLL(ctypes.util.find_library('zstd'))
zstd.ZSTD_compressBound.argtypes=[ctypes.c_size_t];zstd.ZSTD_compressBound.restype=ctypes.c_size_t
zstd.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];zstd.ZSTD_compress.restype=ctypes.c_size_t
zstd.ZSTD_isError.argtypes=[ctypes.c_size_t];zstd.ZSTD_isError.restype=ctypes.c_uint
capacity=zstd.ZSTD_compressBound(len(data));dest=ctypes.create_string_buffer(capacity);source=ctypes.create_string_buffer(data)
length=zstd.ZSTD_compress(dest,capacity,source,len(data),3)
if zstd.ZSTD_isError(length):raise RuntimeError('zstd compression failed')
(lib/'kernel_sm_80.cubin.zst').write_bytes(dest.raw[:length])
(folder/'build_config.json').write_text(json.dumps({'source_root':str(original/'source'),'compiler':'/usr/local/cuda-12.2/bin/nvcc','version':'12.2.140','architecture':'sm_80','options':['-m64','--cubin','--gpu-architecture=sm_80','--use_fast_math','-DNVCC'],'source_entry':'kernel/device/cuda/kernel.cu','source_modified':False,'cycles_version':'Blender 4.2.10 existing runtime','label':'local_a100_cuda122_v1','purpose':'Existing runtime lacks sm_80 cubin; bundled PTX is unsupported by installed driver 535.247.01'},indent=2))
(folder/'README.md').write_text('复用 Blender 4.2.10 自带的未修改 Cycles CUDA 源码，使用已安装 nvcc 12.2.140 编译 sm_80 原生内核。编译命令与来源见 build_config.json；原始编译日志保留。其余运行资源仅使用路径符号链接，未复制数据/模型，未修改原 Blender、驱动或全局配置。通过进程内 _cycles.init 指向此独立运行目录。该硬件兼容适配不属于 H/M 候选。未执行文件指纹或哈希验证。\n')
print('kernel bytes',len(data),'compressed bytes',length)
