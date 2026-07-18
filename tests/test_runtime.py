import os
import pathlib
import subprocess
import sys
import tempfile
import textwrap
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class RuntimeTests(unittest.TestCase):
    def test_application_imports_and_answers_health_request(self):
        with tempfile.TemporaryDirectory() as directory:
            env = os.environ.copy()
            env.update({
                'BACKEND_SECRET_KEY': 'test-backend-secret',
                'CSV_PATH': os.path.join(directory, 'vocabs.csv'),
                'DOWNLOAD_FOLDER': directory,
                'FLASK_APP': 'app',
                'FULL_CHAIN': '',
                'JWT_ACCESS_TOKEN_EXPIRES': '900',
                'JWT_ERROR': 'jwt_error',
                'JWT_REFRESH_TOKEN_EXPIRES': '2592000',
                'JWT_SECRET_KEY': 'test-jwt-secret',
                'JWT_TOKEN_ARGUMENT_NAME': 'access_token',
                'PRIVATE_KEY': '',
                'SMTP_PASSWORD': 'test-password',
                'SMTP_PORT': '587',
                'SMTP_SERVER': 'localhost',
                'SMTP_USER': 'test-user',
                'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
                'SQLALCHEMY_ECHO': 'False',
                'SQLALCHEMY_TRACK_MODIFICATIONS': 'False',
                'UPLOAD_FOLDER': directory,
            })
            result = subprocess.run(
                [
                    sys.executable,
                    '-c',
                    textwrap.dedent(
                        '''
                        import json

                        import app

                        client = app.app.test_client()
                        response = client.post('/test')
                        assert response.status_code == 200
                        assert json.loads(response.get_data(as_text=True)) == {
                            'success': True,
                        }
                        '''
                    ),
                ],
                cwd=ROOT,
                env=env,
                capture_output=True,
                text=True,
                timeout=30,
            )

        self.assertEqual(
            result.returncode,
            0,
            msg='stdout:\n{}\nstderr:\n{}'.format(
                result.stdout, result.stderr),
        )

    def test_service_uses_uv_environment_without_conda(self):
        service = (ROOT / 'deepvocab.service').read_text(encoding='utf-8')
        self.assertIn(
            '/home/ubuntu/dev/deep_vocab_backend/.venv/bin/gunicorn',
            service,
        )
        self.assertIn('--worker-class gthread', service)
        self.assertIn('--no-control-socket', service)
        self.assertNotIn('conda', service)


if __name__ == '__main__':
    unittest.main()
