from botlibs.trigonometry import VectorHashMap, Vector


HASH_MAP_NORMS = VectorHashMap(func_to_cache=lambda v: v.norm2)
X_MAX = 16000
Y_MAX = 9000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]

