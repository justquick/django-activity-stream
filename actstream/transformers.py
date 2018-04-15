class DefaultVerbTransformer(object):
    verb_map = {}

    def trans(self, value):
        return self.verb_map.get(value, value)
