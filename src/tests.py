from click.testing import CliRunner
from r2d2_c3po_brain import geometric_series_sum, get_graph_from_sqlite_r2d2, r2d2


def test_geometric_series_sum_inf():
    result = geometric_series_sum(float('inf'))
    assert int(1 - result) == 0, "La somme pour k = inf devrait donner prob = 0"


def test_geometric_series_sum_0():
    result = geometric_series_sum(0)
    prob = round((1 - result) * 100)
    assert prob == 100, "La somme pour k = 0 devrait donner prob = 100"


def test_geometric_series_sum_1():
    result = geometric_series_sum(1)
    prob = round((1 - result) * 100)
    assert prob == 90, "La somme pour k = 1 devrait donner prob = 90"


def test_geometric_series_sum_2():
    result = geometric_series_sum(2)
    prob = round((1 - result) * 100)
    assert prob == 81, "La somme pour k = 2 devrait donner prob = 81"


def test_geometric_series_sum_3():
    result = geometric_series_sum(3)
    prob = round((1 - result) * 100)
    assert prob == 73, "La somme pour k = 2 devrait donner prob = 73"


def test_get_graph_from_sqlite():
    graph = get_graph_from_sqlite_r2d2("test_data/universe.db", 'Endor')
    ground_value = {
        'Tatooine': {'Dagobah': 6, 'Hoth': 6},
        'Dagobah': {'Tatooine': 6, 'Endor': 4, 'Hoth': 1},
        'Endor': {}, 'Hoth': {'Dagobah': 1, 'Endor': 1, 'Tatooine': 6}}
    assert graph == ground_value, """ the graph should be{
        'Tatooine': {'Dagobah': 6, 'Hoth': 6}, 
        'Dagobah': {'Tatooine': 6, 'Endor': 4, 'Hoth': 1},
        'Endor': {}, 'Hoth': {'Dagobah': 1, 'Endor': 1, 'Tatooine': 6}}"""


def test_shortest_path_1():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/millenium.json', 'test_data/empire1.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '0', "the right answer here is that there is no path that can make it in time"


def test_shortest_path_2():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/millenium.json', 'test_data/empire2.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '81', "the minimum bounty hunters will see here is 2"


def test_shortest_path_3():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/millenium.json', 'test_data/empire3.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '90', "the minimum bounty hunters will see here is 1"


def test_shortest_path_4():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/millenium.json', 'test_data/empire4.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '100', "the minimum bounty hunters will see here is 0"


def test_shortest_path_5():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/millenium.json', 'test_data/empire5.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '73', "the minimum bounty hunters will see here is 3"


def test_shortest_path_8():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/obiwa.json', 'test_data/nutegunray.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '90', "the minimum bounty hunters will see here is 1"


def test_shortest_path_9():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/qwigon.json', 'test_data/nutegunray.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '100', "the minimum bounty hunters will see here is 0"


def test_shortest_path_10():
    runner = CliRunner()

    result = runner.invoke(r2d2, ['test_data/qwigon.json', 'test_data/dooku.json'])
    assert result.exit_code == 0
    assert result.output.strip() == '90', "the minimum bounty hunters will see here is 1"
