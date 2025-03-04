class ObjectFactoryBase:
    def __init__(self):
        ...

    def get_creatable_objects(self):
        return []
    
    def create_object(self,object_type,location):
        return None


def set_object_factory(factory:ObjectFactoryBase):
    global _object_factory
    _object_factory=factory
    
def object_factory() -> ObjectFactoryBase:
    global _object_factory
    return _object_factory

    