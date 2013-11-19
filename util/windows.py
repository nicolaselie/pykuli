import os
import pythoncom
from win32com.shell import shell, shellcon

def get_shortcut_target (filename):
    link = pythoncom.CoCreateInstance (shell.CLSID_ShellLink,    
                                        None,
                                        pythoncom.CLSCTX_INPROC_SERVER,    
                                        shell.IID_IShellLink)
    link.QueryInterface (pythoncom.IID_IPersistFile).Load(filename)
    return link.GetPath (shell.SLGP_UNCPRIORITY)[0]
    
def list_startmenu_applications ():
    startmenu_all = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_COMMON_PROGRAMS)
    startmenu_user = shell.SHGetSpecialFolderPath(0, shellcon.CSIDL_PROGRAMS)
    
    for p in [startmenu_all, startmenu_user]:
        for dirpath, dirnames, filenames in os.walk(p):
            for filename in [os.path.join(dirpath, f) for f in filenames if os.path.splitext(f)[1] == ".lnk"]:
                target = get_shortcut_target(filename)
                if os.path.splitext(target)[1] in [".exe", ".bat", ".cmd"]:
                    yield os.path.splitext(os.path.basename(filename))[0], target
