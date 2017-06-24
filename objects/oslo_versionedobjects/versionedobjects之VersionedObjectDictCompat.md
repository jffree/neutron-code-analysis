# versionedobjects 之 VersionedObjectDictCompat

mixin 类，提供以字典的形式访问 object 的 field。

我直接把源码贴出来吧

```
class VersionedObjectDictCompat(object):
    """Mix-in to provide dictionary key access compatibility

    If an object needs to support attribute access using
    dictionary items instead of object attributes, inherit
    from this class. This should only be used as a temporary
    measure until all callers are converted to use modern
    attribute access.
    """

    def __iter__(self):
        for name in self.obj_fields:
            if (self.obj_attr_is_set(name) or
                    name in self.obj_extra_fields):
                yield name

    iterkeys = __iter__

    def itervalues(self):
        for name in self:
            yield getattr(self, name)

    def iteritems(self):
        for name in self:
            yield name, getattr(self, name)

    if six.PY3:
        # NOTE(haypo): Python 3 dictionaries don't have iterkeys(),
        # itervalues() or iteritems() methods. These methods are provided to
        # ease the transition from Python 2 to Python 3.
        keys = iterkeys
        values = itervalues
        items = iteritems
    else:
        def keys(self):
            return list(self.iterkeys())

        def values(self):
            return list(self.itervalues())

        def items(self):
            return list(self.iteritems())

    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        setattr(self, name, value)

    def get(self, key, value=_NotSpecifiedSentinel):
        if key not in self.obj_fields:
            raise AttributeError("'%s' object has no attribute '%s'" % (
                self.__class__, key))
        if value != _NotSpecifiedSentinel and not self.obj_attr_is_set(key):
            return value
        else:
            return getattr(self, key)

    def update(self, updates):
        for key, value in updates.items():
            setattr(self, key, value)
```

这个 mixin 类应该和 `VersionedObject` 类同时使用，`VersionedObjetc` 提供 `obj_fields` 属性（属性方法），`VersionedObjectDictCompat` 提供对该属性的字典化的处理。