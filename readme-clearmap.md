## Raw data is at 

```
https://osf.io/q6atb/
```

## try installing with pip

python -m venv clearmap_env

#python=3.7
pip
spyder
vispy
pyopengl
natsort
tifffile
pyqtgraph
opencv
cython
matplotlib
scipy
scikit-image
scikit-learn
graph-tool
pytorch

## Update macOS clang to allow using openmp

```
brew update
brew install llvm libomp
```

llvm should be in `/usr/local/opt/llvm/include`

`libomp` installs `open-mpi`

## Trying to get Clear Map to run, basically trying to get pyython include statements to work and auto compile using gcc/clang

editing the following file

/Users/cudmore/opt/anaconda3/envs/ClearMap/lib/python3.7/distutils/unixccompiler.py

Edit compile to point -fopenmp to correct binary, for example

'-I/usr/local/opt/llvm/include -fopenmp'


```
    def _compile(self, obj, src, ext, cc_args, extra_postargs, pp_opts):
        compiler_so = self.compiler_so
        if sys.platform == 'darwin':
            compiler_so = _osx_support.compiler_fixup(compiler_so,
                                                    cc_args + extra_postargs)
        print('=== abb in unixcompiler.py')
        print('   abb we are in python3.7/distutils/unixcompiler.py')
        print('   abb compiler_so:', compiler_so)
        print('   abb cc_args:', cc_args)
        print('   abb src:', src)
        print('   abb obj:', obj)
        print('   abb extra_postargs:', extra_postargs)
        #extra_postargs = extra_postargs[0:-1] # remove -fopenmp
        # -I/usr/local/opt/llvm/include
        print('   extra_postargs is now as follows, this is too much to fix !!!!!!!!!!!!!')
        if extra_postargs:
        	extra_postargs[-1] = '-I/usr/local/opt/llvm/include' + ' ' + '-fopenmp'
        print('   new extra_postargs:', extra_postargs)

```

Edit linking to point -fopenmp to correct binary, for example

'-I/usr/local/opt/llvm/include -fopenmp'

```
    def link(self, target_desc, objects,
             output_filename, output_dir=None, libraries=None,
             library_dirs=None, runtime_library_dirs=None,
             export_symbols=None, debug=0, extra_preargs=None,
             extra_postargs=None, build_temp=None, target_lang=None):

		...
		...
                print('abb linker:', linker)
                print('  abb ld_args:', ld_args)
                if ld_args:
        	        if ld_args[-1] == '-fopenmp':
        	        	ld_args[-1] = '-I/usr/local/opt/llvm/include' + ' ' + '-fopenmp'
                print('  abb new ld_args:', ld_args)

                self.spawn(linker + ld_args)

```

after some editing and moving forward, getting error

use this to open file

```
open ~/opt/anaconda3/envs/ClearMap/lib/python3.7/distutils/spawn.py
```

this is the error

```
~/opt/anaconda3/envs/ClearMap/lib/python3.7/distutils/spawn.py in _spawn_posix(cmd, search_path, verbose, dry_run)
    158                           "command %r failed with exit status %d"
--> 159                           % (cmd, exit_status))
    160             elif os.WIFSTOPPED(status):

DistutilsExecError: command 'g++' failed with exit status 1
```

## Links

Enable OpenMP support in clang in Mac OS X (sierra & Mojave)

https://stackoverflow.com/questions/43555410/enable-openmp-support-in-clang-in-mac-os-x-sierra-mojave

Compile OpenMP programs with gcc compiler on OS X Yosemite

https://stackoverflow.com/questions/29057437/compile-openmp-programs-with-gcc-compiler-on-os-x-yosemite
