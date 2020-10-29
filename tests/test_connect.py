from src.router import route
from click.testing import CliRunner

weyland_return = """Welcome to Weyland Yutani Refreshments, please select a purchase
Gear
```
+-------------+-------+---------+
| Stat        | 1     | 2       |
+=============+=======+=========+
| Name        | Pepsi | Cheetos |
+-------------+-------+---------+
| Cost (eb)   | 50    | 20      |
+-------------+-------+---------+
| Weight (kg) | .5    | .3      |
+-------------+-------+---------+
```
Weapons
```
+----------------+---------------------+-----------------------+
| Stat           | 3                   | 4                     |
+================+=====================+=======================+
| Name           | Malorian Sliver Gun | Federated Arms Impact |
+----------------+---------------------+-----------------------+
| Cost (eb)      | 372                 | 60                    |
+----------------+---------------------+-----------------------+
| Type           | P                   | P                     |
+----------------+---------------------+-----------------------+
| Accuracy       | +0                  | +1                    |
+----------------+---------------------+-----------------------+
| Concealability | J                   | J                     |
+----------------+---------------------+-----------------------+
| Availability   | P                   | E                     |
+----------------+---------------------+-----------------------+
| Damage/Ammo    | 2d6x1d6/2*(Sliver)  | 1d6(.22)              |
+----------------+---------------------+-----------------------+
| #Shots         | 7                   | 10                    |
+----------------+---------------------+-----------------------+
| Rate of Fire   | 2                   | 2                     |
+----------------+---------------------+-----------------------+
| Reliability    | UR                  | VR                    |
+----------------+---------------------+-----------------------+
| Range          | 40m                 | 50m                   |
+----------------+---------------------+-----------------------+
```
Or q to quit
"""

def test_connect_info():
    runner = CliRunner()
    result = runner.invoke(route, ['--character','test','connect','Night City Tourism'])
    assert result.output == \
"""Night City offers a variety of exciting places to visit! To learn more, select one
1) The Sewers
2) The Docks
Or q to quit
"""
    runner.invoke(route, ['--character','test','connect','tourism','--cmds','q'])


def test_connect_info_submenu():
    runner = CliRunner()
    runner.invoke(route, ['--character','test','connect','Night City Tourism'])
    result = runner.invoke(route, ['--character','test','connect','tourism','--cmds','1'])
    assert """The sewers are incredibly scenic""" in result.output
    result = runner.invoke(route, ['--character','test','connect','tourism','--cmds','2'])
    assert """The Docks are next to water""" in result.output
    result = runner.invoke(route, ['--character','test','connect','tourism','--cmds','q'])
    assert """Goodbye""" in result.output


def test_connect_shop():
    runner = CliRunner()
    result = runner.invoke(route, ['--character','test','connect','Weyland Yutani Refreshments'])
    assert  weyland_return == result.output
    result = runner.invoke(route, ['--character','test','connect','weyland','--cmds','q'])


def test_connect_shop_fuzzy_name():
    runner = CliRunner()
    result = runner.invoke(route, ['--character','test','connect','weyland'])
    assert weyland_return == result.output
    result = runner.invoke(route, ['--character','test','connect','weyland','--cmds','q'])
