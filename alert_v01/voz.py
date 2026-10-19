import asyncio
import ctypes
import os
import tempfile

import edge_tts

# Voz neural pt-BR (Francisca) disponibilizada pelo Edge TTS.
VOZ = "pt-BR-FranciscaNeural"

# Normalização dos nomes de núcleo/produto: a chave é o nome sem acentos e em
# minúsculas (como vem do dashboard) e o valor é a forma correta para fala em pt-BR.
NOMES_NUCLEOS = {
    'agricola': 'Agrícola',
    'configuracao de balanca e bastao': 'Configuração de balança e bastão',
    'pmg e comunicacao para associacao': 'PMG e Comunicação para Associação',
    'reproducao': 'Reprodução',
    'csi': 'C S I',
    'sisbov': 'Sisbov',
}

# Cache de áudio já sintetizado: texto -> caminho do arquivo mp3.
_CACHE_AUDIO = {}


def _nome_para_fala(nome_nucleo):
    # O título vem como "Núcleo - <contato/número>"; falamos apenas o núcleo,
    # nunca o restante (que pode conter o número do contato).
    base = nome_nucleo.split(' - ')[0].strip()
    return NOMES_NUCLEOS.get(base.lower(), base)


def _sintetizar(texto):
    caminho = _CACHE_AUDIO.get(texto)
    if caminho and os.path.exists(caminho):
        return caminho
    fd, caminho = tempfile.mkstemp(prefix='francisca_', suffix='.mp3')
    os.close(fd)
    asyncio.run(edge_tts.Communicate(texto, VOZ).save(caminho))
    _CACHE_AUDIO[texto] = caminho
    return caminho


def _reproduzir(caminho):
    winmm = ctypes.windll.winmm.mciSendStringW
    alias = 'francisca_tts'
    winmm(f'open "{caminho}" type mpegvideo alias {alias}', None, 0, None)
    winmm(f'play {alias} wait', None, 0, None)
    winmm(f'close {alias}', None, 0, None)


def anunciar_cliente(nome_nucleo):
    nome = _nome_para_fala(nome_nucleo)
    caminho = _sintetizar(f"Atenção! Cliente aguardando no núcleo {nome}")
    _reproduzir(caminho)


def listar_vozes():
    vozes = asyncio.run(edge_tts.list_voices())
    for voz in vozes:
        if voz.get('Locale', '').startswith('pt-BR'):
            print(voz['ShortName'], '-', voz.get('Gender'))


if __name__ == '__main__':
    listar_vozes()
