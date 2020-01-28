def get_value(path, data):
    _path = path.split('.')
    _rv = data
    for p in _path:
        if isinstance(_rv, dict):
            _rv = _rv.get(p)
        else:
            return None
    return _rv
