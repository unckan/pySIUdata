![Build Status](https://github.com/unckan/pySIUdata/actions/workflows/test.yml/badge.svg)
[![GitHub All Releases](https://img.shields.io/github/downloads/unckan/pySIUdata/total)](https://github.com/unckan/pySIUdata/releases)
[![GitHub Issues](https://img.shields.io/github/issues/unckan/pySIUdata)](https://github.com/unckan/pySIUdata/issues)
[![GitHub PR](https://img.shields.io/github/issues-pr/unckan/pySIUdata)](https://github.com/unckan/pySIUdata/pulls)
[![Licence](https://img.shields.io/github/license/unckan/pySIUdata)](https://github.com/unckan/pySIUdata/blob/master/LICENSE)
[![PyPi version](https://img.shields.io/pypi/v/siu-data)](https://pypi.org/project/siu-data/)
[![Pypi py version](https://img.shields.io/pypi/pyversions/siu-data)](https://pypi.org/project/siu-data/)
[![Last Commit](https://img.shields.io/github/last-commit/unckan/pySIUdata)](https://github.com/unckan/pySIUdata/commits/master)

# py SIU data
Obtener datos de sistemas SIU

Instalar

```
pip install siu-data
```

## Portal de Transparencia

Obtención de datos del portal de transparencia.

Ejemplo de uso

``` python
from siu_data.portal_data import SIUPoratlTransparenciaData

s = SIUPoratlTransparenciaData(base_url='http://wichi.siu.edu.ar/pentaho/plugin/cda/api/doQuery',
                               username='usuario_transparencia',
                               password='clave_transparencia')
s.load_all_data()
s.save_metadata('lala.csv')
```

## Tests

```
python -m pytest
```
