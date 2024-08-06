from app.models.instance import Person, Instance
from app.services.r_indicators import compR3_2

def test_compR3_2_with_authors_present():
    # Case where authors are present
    authors = [
        Person(name='Alice Smith', type='author', email='alice@example.com'),
        Person(name='Bob Jones', type='author', email='bob@example.com')
    ]
    instance = Instance(authors=authors)
    result, logs = compR3_2(instance)
    assert result == True

def test_compR3_2_with_no_authors():
    # Case where no authors are present
    instance = Instance(authors=[])
    result, logs = compR3_2(instance)
    assert result == False

def test_compR3_2_with_authors_none():
    # Case where authors is None
    instance = Instance(authors=None)
    result, logs = compR3_2(instance)
    assert result == False

def test_compR3_2_with_authors_empty_person():
    # Case where authors list contains a Person with empty email
    authors = [Person(name='Alice Smith', type='author', email='')]
    instance = Instance(authors=authors)
    result, logs = compR3_2(instance)
    assert result == True

def test_compR3_2_with_authors_mixed_values():
    # Case where authors list contains both valid and empty email Person
    authors = [
        Person(name='Alice Smith', type='author', email='alice@example.com'),
        Person(name='Bob Jones', type='author', email=''),
        Person(name='Charlie Brown', type='author')
    ]
    instance = Instance(authors=authors)
    result, logs = compR3_2(instance)
    assert result == True