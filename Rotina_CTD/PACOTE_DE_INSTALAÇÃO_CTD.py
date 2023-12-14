# Essa é uma rotina de instalação de todos os pacotes necessários para a utilização do Sistema de Automação de Processamento de Dados coletados pelo aparelho CTD.
# Além desses pacotes do python instalados, é necessário possuir o Software da SeaBird (SBEDataProcessing-Win32) para realizar o Processamento.

try:
    from pathlib import Path
except ImportError:
    print("A biblioteca 'pathlib' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pathlib'])
    from pathlib import Path

try:
    import glob
except ImportError:
    print("A biblioteca 'glob' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'glob'])
    import glob

try:
    import shutil
except ImportError:
    print("A biblioteca 'shutil' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'shutil'])
    import shutil

try:
    import subprocess
except ImportError:
    print("A biblioteca 'subprocess' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'subprocess'])

try:
    import os
except ImportError:
    print("A biblioteca 'os' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'os'])

try:
    import re
except ImportError:
    print("A biblioteca 're' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 're'])

try:
    import lxml
except ImportError:
    print("A biblioteca 'lxml' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'lxml'])
    import lxml

try:
    import sys
except ImportError:
    print("A biblioteca 'sys' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'sys'])

try:
    import html
except ImportError:
    print("A biblioteca 'html' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'html'])
    import html

from lxml import etree

try:
    import chardet
except ImportError:
    print("A biblioteca 'chardet' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'chardet'])
    import chardet

try:
    import simplekml
except ImportError:
    print("A biblioteca 'simplekml' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'simplekml'])
    import simplekml

try:
    from collections import defaultdict
except ImportError:
    print("A biblioteca 'collections' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'collections'])
    from collections import defaultdict
