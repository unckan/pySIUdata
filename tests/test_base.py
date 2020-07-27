import os
from siu_data.portal_data import SIUPoratlTransparenciaData


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

    @classmethod
    def teardown_class(cls):
        pass    

    def test_query_files_list(self):
        qf = self.siudata.get_query_files()
        assert len(qf), self.total_query_files
    
    def test_load_all(self):
        self.siudata.load_all_data()
        assert len(self.siudata.query_files), self.total_query_files
