from botlibs.trigonometry import HashMapNorms, Vector

HASH_MAP_NORMS = HashMapNorms(norm_name="norm2")

MY_OWNER = 1
FOE_OWNER = 2

X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]
