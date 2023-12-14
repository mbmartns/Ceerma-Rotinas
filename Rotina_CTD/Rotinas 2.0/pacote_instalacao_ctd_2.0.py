import subprocess
import sys

# Bibliotecas a serem instaladas
libraries = [
    'html',
    'simplekml',
    'shutil',
    'os',
    'numpy',
    'xml.etree.ElementTree',
    'pandas',
    'lxml',
    'glob',
    're',
    'subprocess',
    'matplotlib',
    'chardet',
    'cartopy',
    'pathlib',
    'collections'
]


# Função para verificar e instalar uma biblioteca usando o pip
def install_with_pip(library):
    try:
        __import__(library)
    except ImportError:
        print(f"A biblioteca '{library}' não está instalada. Instalando agora...")
        subprocess.check_call(['pip', 'install', library])

# Função para verificar e instalar uma biblioteca usando o conda
def install_with_conda(library):
    try:
        __import__(library)
    except ImportError:
        print(f"A biblioteca '{library}' não está instalada. Instalando agora...")
        subprocess.check_call(['conda', 'install', '-y', library])

# Verifica se o sistema operacional está rodando Anaconda
is_anaconda = 'conda' in sys.version or 'Continuum' in sys.version or 'Anaconda' in sys.version

# Instalação das bibliotecas usando o pacote correspondente
for library in libraries:
    if is_anaconda:
        install_with_conda(library)
    else:
        install_with_pip(library)
