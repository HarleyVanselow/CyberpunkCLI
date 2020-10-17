from src.router import query_character


def test_query_character():
    assert ('B22', '8', 'Charismatic Leadership') == query_character(
        'harley', 'charisma')
