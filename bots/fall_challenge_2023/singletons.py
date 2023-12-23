from botlibs.trigonometry import HashMapNorms, Vector, Point

HASH_MAP_NORMS = HashMapNorms(norm_name="norm2")

MY_OWNER = 1
FOE_OWNER = 2

X_MIN = 0
Y_MIN = 0
X_MAX = 10000
Y_MAX = 10000
D_MAX = HASH_MAP_NORMS[Vector(X_MAX, Y_MAX)]

MAP_CENTER = Point(X_MAX / 2, Y_MAX / 2)
CORNERS = {"TL": Point(X_MIN, Y_MIN + 2500),
           "TR": Point(X_MAX, Y_MIN + 2500),
           "BR": Point(X_MAX, Y_MAX),
           "BL": Point(X_MIN, Y_MAX)}
