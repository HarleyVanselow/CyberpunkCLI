from src.router import route
from click.testing import CliRunner
import shlex
runner = CliRunner()
try:
	result = runner.invoke(route, shlex.split('--character harley roll attack impact spitfyre 5'), catch_exceptions=False)
	print(result.output)
except Exception as e:
	print(e)