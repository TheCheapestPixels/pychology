class Blackboard:
    def __init__(self, parent=None, **kwargs):
        self.parent = parent
        self.values = {}

    def __setitem__(self, key, value):
        if key in self.values:
            self.values[key] = value
        elif (self.parent is not None) and (key in self.parent):
                self.parent[key] = value
        else:
            self.values[key] = value

    def __contains__(self, key):
        if key in self.values:
            return True
        if self.parent is not None:
            return key in self.parent
        return False

    def __getitem__(self, key):
        if key in self.values:
            return self.values[key]
        if (self.parent is not None) and (key in self.parent):
            return self.parent[key]
        raise KeyError

    def __delitem__(self, key):
        if key in self.values:
            del self.values[key]
        else:
            raise KeyError

# is_value / is_func


# bb.get('foo', None, 'bar') returns [] for path foo.*.bar
