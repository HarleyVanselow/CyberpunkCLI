from src.router import route
from click.testing import CliRunner
import shlex
runner = CliRunner()
result = runner.invoke(route, shlex.split('--character spitfyre roll skillcheck --stat int'))
print(result.output)