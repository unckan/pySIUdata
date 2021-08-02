import os
import pytest
from siu_data.portal_data import SIUPoratlTransparenciaData
from siu_data.query_file import SIUTranspQueryFile

@pytest.mark.vcr()
class TestBasic:

    @classmethod
    def setup_class(cls):
        cls.siudata = SIUPoratlTransparenciaData(
                                base_url='http://wichi.siu.edu.ar/pentaho/plugin/cda/api/doQuery',
                                username='usuario_transparencia',
                                password='clave_transparencia')
        
        qfolder = 'siu_data/queries'
        tqf = 0
        for f in os.listdir(qfolder):
            path = os.path.join(qfolder, f)
            if os.path.isfile(path):
                ext = f.split('.')[-1]
                if ext == 'json':
                    tqf += 1
        
        cls.total_query_files = tqf
        cls.results_folder_path = 'results'
        if not os.path.isdir(cls.results_folder_path):
            os.makedirs(cls.results_folder_path)

    @classmethod
    def teardown_class(cls):
        pass    

    def test_query_files_list(self):
        qf = self.siudata.get_query_files()
        assert len(qf), self.total_query_files
    
    def test_load_all(self):
        self.siudata.load_all_data()
        assert len(self.siudata.query_files), self.total_query_files

    def test_request_all(self):
        report = [] 
        errores = 0
        datasets_ok = 0
        for qf in self.siudata.query_files:
            stqf = SIUTranspQueryFile(portal=self.siudata, path=qf)
            # open to read query params
            stqf.open()
            # request all data
            stqf.request_all(results_folder_path=self.results_folder_path)
            for err in stqf.errors:
                errores += 1
                print('Error: {}'.format(err))

            report += stqf.requests
            for dataset in stqf.datasets:
                datasets_ok += 1
                print('Dataset {}'.format(dataset['name']))

        expected_datasets = 201
        expected_errors = 27

        if expected_datasets != datasets_ok:
            print('Fail counting datasets')
            
        if expected_errors != errores:
            print('Fail counting errors')

        if expected_datasets != datasets_ok or expected_errors != errores:
            print(report)
        
        assert datasets_ok == expected_datasets
        assert errores == expected_errors
        