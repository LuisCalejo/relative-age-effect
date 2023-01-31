def install_packages(packages):
    import sys
    import subprocess
    import os
    import bpy

    # Install packages into Blender:
    def python_exec():
        import os
        import bpy
        try:
            # 2.92 and older
            path = bpy.app.binary_path_python
        except AttributeError:
            # 2.93 and later
            import sys
            path = sys.executable
        return os.path.abspath(path)

    try:
        from pandas import read_csv
    except:
        python_exe = python_exec()
        # upgrade pip
        subprocess.call([python_exe, "-m", "ensurepip"])
        subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
        # install required packages
        for package in packages:
            subprocess.call([python_exe, "-m", "pip", "install", package])
            # subprocess.call([python_exe, "-m", "pip", "install", "pandas"])
            # subprocess.call([python_exe, "-m", "pip", "install", "math"])
            # subprocess.call([python_exe, "-m", "pip", "install", "random"])
            # subprocess.call([python_exe, "-m", "pip", "install", "numpy"])
            # subprocess.call([python_exe, "-m", "pip", "install", "datetime"])