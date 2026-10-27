"""Build-time adapter only; the packaged app has no Python dependency."""
from pathlib import Path
import re,subprocess,sys,tempfile,shutil
app=Path(sys.argv[1])
for path in (app/'Contents/MacOS/dialogue-worker',app/'Contents/Frameworks/libdialogue_separator.dylib',app/'Contents/Frameworks/libonnxruntime.1.31.1.dylib'):
    # Fat slices have different build rpaths. install_name_tool requires a removed
    # rpath to exist in every slice, so edit each slice separately, then recombine.
    with tempfile.TemporaryDirectory(prefix='bundle-paths-') as directory:
        slices=[]
        for arch in ('arm64','x86_64'):
            thin=Path(directory)/arch
            subprocess.run(['lipo',str(path),'-thin',arch,'-output',str(thin)],check=True)
            output=subprocess.check_output(['otool','-l',str(thin)],text=True)
            rpaths=set(re.findall(r'cmd LC_RPATH\s+cmdsize \d+\s+path (.+?) \(offset',output))
            for item in sorted(rpaths):subprocess.run(['install_name_tool','-delete_rpath',item,str(thin)],check=True)
            relative='@executable_path/../Frameworks' if path.parent.name=='MacOS' else '@loader_path'
            subprocess.run(['install_name_tool','-add_rpath',relative,str(thin)],check=True)
            dependencies=subprocess.check_output(['otool','-L',str(thin)],text=True)
            for dependency in re.findall(r'(@rpath/libonnxruntime[^\s]+)',dependencies):
                if dependency!='@rpath/libonnxruntime.1.31.1.dylib':
                    subprocess.run(['install_name_tool','-change',dependency,'@rpath/libonnxruntime.1.31.1.dylib',str(thin)],check=True)
            if path.suffix=='.dylib':subprocess.run(['install_name_tool','-id','@rpath/'+path.name,str(thin)],check=True)
            slices.append(str(thin))
        subprocess.run(['lipo','-create',*slices,'-output',str(path)],check=True)
