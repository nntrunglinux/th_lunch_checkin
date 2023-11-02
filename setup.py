import os
import sys
from cx_Freeze import setup, Executable
from constants import VERSION, IMAGES_DIR, UI_DIR


icon_path = os.path.join(IMAGES_DIR, 'icon.ico')
files = [IMAGES_DIR, UI_DIR]
base = "Win32GUI" if sys.platform == "win32" else None


target = Executable(
    script='main.py',
    base=base,
    icon=icon_path,
    target_name='lunchcheckin'
)


build_exe_options = {
    'include_files': files,
    'build_exe': f"TH_LUNCHCHECKIN_TOOL_{VERSION}"
}


setup(
    name="LunchCheckin",
    version=VERSION,
    description="Lunch checkin tool",
    options={"build_exe": build_exe_options},
    executables=[target]
)
