import unittest
from airflow.models import DagBag

class TestDags(unittest.TestCase):
    def setUp(self):
        self.dagbag = DagBag()

    def test_dag_integrity(self):
        dags_with_errors = []
        for dag_id, dag in self.dagbag.dags.items():
            dag_test = self.dagbag.process_file(dag.fileloc)
            if dag_test.import_errors:
                dags_with_errors.append(dag_id)

        self.assertEqual([], dags_with_errors)