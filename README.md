![Build Status](https://github.com/avdata99/pySIUdata/actions/workflows/test.yml/badge.svg)
[![GitHub All Releases](https://img.shields.io/github/downloads/avdata99/pySIUdata/total)](https://github.com/avdata99/pySIUdata/releases)
[![GitHub Issues](https://img.shields.io/github/issues/avdata99/pySIUdata)](https://github.com/avdata99/pySIUdata/issues)
[![GitHub PR](https://img.shields.io/github/issues-pr/avdata99/pySIUdata)](https://github.com/avdata99/pySIUdata/pulls)
[![Licence](https://img.shields.io/github/license/avdata99/pySIUdata)](https://github.com/avdata99/pySIUdata/blob/master/LICENSE)
[![PyPi version](https://img.shields.io/pypi/v/siu-data)](https://pypi.org/project/siu-data/)
[![Pypi py version](https://img.shields.io/pypi/pyversions/siu-data)](https://pypi.org/project/siu-data/)
[![Last Commit](https://img.shields.io/github/last-commit/avdata99/pySIUdata)](https://github.com/avdata99/pySIUdata/commits/master)

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
