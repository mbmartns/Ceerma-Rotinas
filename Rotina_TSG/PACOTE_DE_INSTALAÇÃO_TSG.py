# Essa é uma rotina de instalação de todos os pacotes necessários para a utilização do Sistema de Automação de Processamento de Dados coletados pelo aparelho TSG.
# Além desses pacotes do python instalados, é necessário possuir o Software da SeaBird (SBEDataProcessing-Win32) para realizar o Processamento.


try:
    import lxml
except ImportError:
    print("A biblioteca 'lxml' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'lxml'])
    import lxml

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
    import matplotlib.pyplot as plt
except ImportError:
    print("A biblioteca 'matplotlib' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'matplotlib'])
    import matplotlib.pyplot as plt

try:
    import cartopy.crs as ccrs
except ImportError:
    print("A biblioteca 'cartopy' não está instalada. Instalando agora...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'cartopy'])
    import cartopy.crs as ccrs
