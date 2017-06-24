# versionedobjects 之 ComparableVersionedObject

提供 object 的比较计算

```
class ComparableVersionedObject(object):
    """Mix-in to provide comparison methods

    When objects are to be compared with each other (in tests for example),
    this mixin can be used.
    """
    def __eq__(self, obj):
        # FIXME(inc0): this can return incorrect value if we consider partially
        # loaded objects from db and fields which are dropped out differ
        if hasattr(obj, 'obj_to_primitive'):
            return self.obj_to_primitive() == obj.obj_to_primitive()
        return NotImplemented

    def __ne__(self, obj):
        if hasattr(obj, 'obj_to_primitive'):
            return self.obj_to_primitive() != obj.obj_to_primitive()
        return NotImplemented

```

