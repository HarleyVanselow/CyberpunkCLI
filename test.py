from src.router import route
from click.testing import CliRunner
import shlex
runner = CliRunner()
try:
	result = runner.invoke(route, shlex.split('--character harley roll attack impact spitfyre 5 --target head --modifiers 2,-2,5'), catch_exceptions=False)
	print(result.output)
except Exception as e:
	print(e)

# from src.sheetio import deal_damage, query_character
# _, wounds, _ = query_character('spitfyre', 'wounds')
# print(wounds)
# deal_damage('spitfyre', 7)