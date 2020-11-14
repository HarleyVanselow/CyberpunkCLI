from src.router import route
from click.testing import CliRunner
import traceback
import shlex
runner = CliRunner()
try:
    # result = runner.invoke(route, shlex.split('--character Koeknee roll attack Colt spitfyre 5'), catch_exceptions=False)
    # result = runner.invoke(route, shlex.split('--character Hubert roll facedown'), catch_exceptions=False)
    # result = runner.invoke(route, shlex.split('--character spitfyre roll attack Federated harley 5'), catch_exceptions=False)
    result = runner.invoke(route, shlex.split('--character Franklin check emp'), catch_exceptions=False)
    print(result.output)
except Exception:
	print(traceback.format_exc())

# from src.sheetio import deal_damage, query_character
# _, wounds, _ = query_character('spitfyre', 'wounds')
# print(wounds)
# deal_damage('spitfyre', 7)