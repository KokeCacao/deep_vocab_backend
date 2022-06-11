from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(session_options={'autocommit': False})

print("Parsing Arguments...")
import argparse
parser = argparse.ArgumentParser(prog="python app.py", description="Launch backend of DeepVocab")
parser.add_argument('--version', action='version', version='%(prog)s v0.1')
parser.add_argument('--verbose', '-v', dest='verbose', action='count', default=0) # -vvv
parser.add_argument('--port', '-p', dest='port', default=5000, type=int, nargs='?', help='port number, default 5000')
parser.add_argument('--host', dest='host', default='0.0.0.0', type=str, nargs='?', help='host address, default 0.0.0.0')
parser.add_argument('--database', '-b', dest='database', default='/home/koke_cacao/Documents/Koke_Cacao/Database/deep_vocab.db', type=str, nargs='?', help='database file location, default /home/koke_cacao/Documents/Koke_Cacao/Database/deep_vocab.db')
parser.add_argument('--csv', '-c', dest='csv', default='/home/koke_cacao/Documents/Koke_Cacao/Python/WorkSpace/Barron3500/巴郎Sat3500-excel-original版(Linux).csv', type=str, nargs='?', help='csv file location, default /home/koke_cacao/Documents/Koke_Cacao/Python/WorkSpace/Barron3500/巴郎Sat3500-excel-original版(Linux).csv')

# args = parser.parse_args()
# compatible with gunicorn (https://stackoverflow.com/questions/32802303/python-flask-gunicorn-error-unrecognized-arguments)
args, unknown = parser.parse_known_args()
