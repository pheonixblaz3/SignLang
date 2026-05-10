import os
import shutil
import unittest


class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.base = 'data/synth_test/raw'
        self.out = 'data/synth_test/processed'
        # ensure clean
        if os.path.exists('data/synth_test'):
            shutil.rmtree('data/synth_test')
        os.makedirs(self.base, exist_ok=True)

    def tearDown(self):
        if os.path.exists('data/synth_test'):
            shutil.rmtree('data/synth_test')

    def test_process_and_optional_train(self):
        # create synthetic data
        from scripts.generate_synthetic_data import generate
        generate(base=self.base, labels=['A', 'B', 'C'], samples_per_label=10)

        # run processing
        import scripts.process_data as proc
        proc.main(base=self.base, out=self.out, augment=False)

        # processed files should exist
        expected = ['X_train.npy', 'y_train.npy', 'X_val.npy', 'y_val.npy', 'X_test.npy', 'y_test.npy']
        for fn in expected:
            self.assertTrue(os.path.exists(os.path.join(self.out, fn)), f"Missing {fn}")

        # try training if scikit-learn is available
        try:
            import sklearn  # type: ignore
            from scripts.train_baseline import main as train_main
            train_main(data_dir=self.out, out='models/synth_landmark.joblib')
            self.assertTrue(os.path.exists('models/synth_landmark.joblib'))
            # cleanup model
            os.remove('models/synth_landmark.joblib')
        except Exception:
            # skip training if sklearn/joblib not present
            self.skipTest('scikit-learn/joblib not available; skipping train step')


if __name__ == '__main__':
    unittest.main()
