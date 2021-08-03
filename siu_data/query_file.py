import csv
import json
import logging
import os
import pyexcel
import requests
from slugify import slugify

logger = logging.getLogger(__name__)


class SIUTranspQueryFile:
    """ Cada uno de los archivos para consultar al portal de transparencia. """

    def __init__(self, portal, path, params={}, timeout=5):
        """ inicializar un archivo de consulta al portal de transparencia
            Params:
                path (str): Path al archivo de consulta
                params (dict): Parámetros de la consulta, se consiguen en 
                    general en la funcion open pero podrían inicializarse aquí
                """
        self.portal = portal
        self.path = path
        self.params = params
        self.timeout = timeout
        self.errors = []
        self.requests = []  # lista de todas las queries hechas
        self.datasets = []  # resultados de todos (puede haber más de uno si hay iterables) los requests hacia el origen
        
    def open(self):
        """ Abrir el archivo y cargar sus parámetros """
        logger.info('Opening Query File {}'.format(self.path))
        try:
            f = open(self.path, 'r')
        except Exception as e:
            error = 'Error abriendo el archivo {}: {}'.format(self.path, e)
            logger.error(error)
            self.errors.append(error)
            return None
        try:
            query = json.load(f)
        except Exception as e:
            error = 'Error parseando a JSON el archivo {}: {}'.format(self.path, e)
            logger.error(error)
            self.errors.append(error)
            return None
        
        f.close()
        self.params = query
        return query
    
    def request_all(self, results_folder_path):
        """ iterar por todos los datos. Usar los iterables definidos.
            Carga self.datasets 
            TODO se podría separar en gather y fetch a futuro"""
        self.datasets = []
        logger.info('Request All from Query File {}'.format(self.params['name']))
        
        if 'iterables' in self.params:
            if "sub_list" in self.params['iterables']:
                sub_list = self.params['iterables']['sub_list']
                self.iterate_sublist(results_folder_path, sub_list=sub_list)
        else:
            data = self.harvest()
            if self.data_is_empty(data):
                logger.info('Dataset vacío: {}'.format(self.params['name']))
                return
            title = self.params['title']
            notes = self.params['notes']
                    
            full = {
                'name': self.params['name'],
                'title': title,
                'notes': notes,
                'data': data,
                'tags': self.build_tags(tags=self.params.get('tags', []))
            }
            full['resources'] = self.save_data(full, results_folder_path)
            self.datasets.append(full)
        
    def iterate_sublist(self, results_folder_path, sub_list={}):
        """ Iterar por una sub-lista de una query que lo requiere
            Esta funcion carga sel.datasets con todos los datos 
                encontrados que no estén vacios.
            La sublista debe ser definida de la forma
            {
                "help": "No requerido pero util para documentar",
                "name": "lala",
                "params": {
                    "paramprm_tablero_visible": "18",
                    "dataAccessId": "param_ua_cargos"
                    }
            }
            """
        name = sub_list['name']
        logger.info('Iterando sublista: {}'.format(name))
        # agregar los nuevos parámetros para la sublista tomando como base la lista original del archivo JSON.
        params = self.params['params'].copy()
        # pisar con los valores requeridos para la sub lista
        params.update(sub_list['params'])
        # quitar el parametro que despues se va a aplicar
        apply_to = sub_list['apply_to']
        del params[apply_to]
        sub_list['params'] = params
        data = self.request_data(query=sub_list)
        # aca recibimos un JSON como en los datasets.
        # interpretamos que resultset tendrá una lista de los valores que buscamos
        if data is None:  # tiene que ser algun error
            elementos = []
        else:
            elementos = data.get('resultset', [])

        # estos valores deben ser pasados al parametro definido en 'apply_to'
        apply_to = sub_list['apply_to']

        for elem in elementos:
            # aqui esperamos una lista de un solo elemento
            value = elem[0]
            if type(value) in [int, float]:
                value = str(value)
            logger.info('Buscando datos para la sublista: {}'.format(value))
            # ahora estoy listo para la cosecha de los datos
            # cada valor obtenido debe pasarse al campo definido en 'apply_to'
            # y cosecharse
            self.params['params'][apply_to] = value

            data = self.harvest()
            if self.data_is_empty(data):
                logger.info('Dataset vacío: {} {}'.format(name, value))
                continue
            logger.info('Datos obtenidos para: {}'.format(value))
            title = self.params['title']
            notes = self.params['notes']
            
            # TODO analizar como transformar algunos valores no válidos 
            # para ser usados como nombres
            if value == '1-TODAS':
                name_value = 'completo'
                title_value = 'Completo'
            else:
                name_value = slugify(value)
                title_value = value
                
            full = {
                'name': '{}-{}'.format(self.params['name'], name_value),
                'title': '{} {}'.format(title, title_value),
                'notes': notes,
                'data': data,
                'tags': self.build_tags(tags=self.params.get('tags', []))
            }
            full['resources'] = self.save_data(full, results_folder_path)
            self.datasets.append(full)

    def request_data(self, query=None):
        """ consultar la URL con los parámetros definidos 
            y devolver el resultado.
            No se requiere en general cargar el parámetro 
            'query' porque se usan los parámetros locales 
            (self.params). Solo se usa para consultas especiales
            (por ejemplo para obetner sublistas) """
        
        if query is None:
            query = self.params
        
        if len(query.keys()) == 0:
            error = 'Error: Intentando leer datos sin los parámetros no cargados'
            logger.error(error)
            self.errors.append(error)
            return None

        name = query['name']
        logger.info('Request data from Query File {}'.format(name))
        
        base_url = self.portal.base_url
        username = self.portal.username
        password = self.portal.password
        params = query['params']
        
        p = self.get_request_uid(params)
        logger.info('Request URL {}, PARAMS: {}'.format(base_url, params))        
        try:
            resp = requests.post(base_url, auth=(username, password), data=params, timeout=self.timeout)  #, headers=headers)
        except Exception as e:
            error = '{} Error en request para obtener datos. Error: {}'.format(p, e)
            logger.error(error)
            self.errors.append(error)
            self.requests.append('{} ERROR request'.format(p))
            return None
        
        try:
            data = resp.json()
        except Exception as e:
            error = '{} JSON error. Error: {} Response: {}'.format(p, e, resp.text[:20])
            logger.error(error)
            self.errors.append(error)
            self.requests.append('{} ERROR JSON'.format(p))
            return None
        
        rows = len(data.get('resultset', []))
        self.requests.append('{} OK ROWS {}'.format(p, rows))
        
        return data
    
    def get_request_uid(self, params):
        """ obtener un resumen identificador de una consulta """
        path = params.get('path', '/no-path')
        upath = path.split('/')[-1]
        udaci = params.get('dataAccessId', 'no-access-id')
        extras = ['{}:{}'.format(k, v) for k, v in params.items() if k.startswith('paramprm')]
        uextras = ' '.join(extras)
        uid = '{} {} {}'.format(upath, udaci, uextras)
        return uid

    def harvest(self):
        """ Lanzar el proceso de cosecha y guardar los resultados para un año específico """
        
        data = self.request_data()
        return data

    def data_is_empty(self, data):
        """ a veces iteramos sobre elementos que dan resultados vacios
            No crear datasets en esos casos """
        
        is_empty = False
        if data is None:  # No hay un JSON para este query
            is_empty = True
        elif len(data.get('resultset', [])) == 0:
            is_empty = True

        return is_empty

    def save_data(self, full, results_folder_path):
        """ grabar los datos a disco """        
        name = full['name']
        title = full['title']
        data = full['data']
        data_str = json.dumps(data, indent=4)
        filename = '{}.json'.format(name)
        save_to = os.path.join(results_folder_path, filename)
        f = open(save_to, 'w')
        f.write(data_str)
        f.close()
        res_json = {
            'title': '{} JSON'.format(title),
            'name': '{}-json'.format(name),
            'upload': save_to,  # TODO no se puede mandar el path en el dict para que se cree solo :(
            'format': 'json'
        }

        # grabar tambien en CSV
        filename = '{}.csv'.format(name)
        save_to = os.path.join(results_folder_path, filename)
        self.json_to_csv(data=data, save_path=save_to)
        res_csv = {
            'title': '{} CSV'.format(title),
            'name': '{}-csv'.format(name),
            'upload': save_to,  # TODO no se puede mandar el path en el dict para que se cree solo :(
            'format': 'csv'
        }

        # grabar tambien en XLS
        filename = '{}.xls'.format(name)
        save_to = os.path.join(results_folder_path, filename)
        self.json_to_xls(data=data, save_path=save_to)
        res_xls = {
            'title': '{} XLS'.format(title),
            'name': '{}-xls'.format(name),
            'upload': save_to,  # TODO no se puede mandar el path en el dict para que se cree solo :(
            'format': 'xls'
        }
        
        # return CKAN resurces
        resources = [res_csv, res_json, res_xls]

        return resources
    
    def json_to_csv(self, data, save_path=None):
        """ transformar los datos JSON a CSV """
        logger.info('JSON to CSV {}'.format(save_path))
        metadata = data['metadata']
        field_names = [md['colName'] for md in metadata]
        rows = data['resultset']

        if save_path is not None:
            f = open(save_path, 'w')
            wr = csv.DictWriter(f, fieldnames=field_names)
            wr.writeheader()

            rows_utf8 = []
            for row in rows:
                row_utf8 = {}
                c = 0
                for field in row:
                    row_utf8[field_names[c]] = field
                    c += 1
                wr.writerow(row_utf8)
                rows_utf8.append(row_utf8)
            f.close()

        return field_names, rows_utf8

    def json_to_xls(self, data, save_path=None):
        """ transformar los datos JSON a CSV """
        logger.info('JSON to XLS {}'.format(save_path))
        metadata = data['metadata']
        field_names = [md['colName'] for md in metadata]
        rows = data['resultset']

        results = []
        for row in rows:
            row_utf8 = {}
            c = 0
            for field in row:
                row_utf8[field_names[c]] = field
                c += 1
            results.append(row_utf8)
            
        if save_path is not None:
            pyexcel.save_as(
                records=results,
                dest_file_name=save_path,
                dest_encoding="UTF-8"
            )

        return field_names, results 
    
    def build_tags(self, tags):
        return [{'name': tag} for tag in tags] 
