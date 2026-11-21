import sys; sys.path.insert(0,'.')
import key_data as k
print(k.get_parallel_key(30))
print(k.get_keyway_depth(30))
print(k.auto_design(30,100,40,'钢','静载荷'))
for f,args in [(k.calc_parallel_key_strength,(30,8,7,40,100,'钢','静载荷')),(k.calc_parallel_key_strength_shear,(30,8,40,100,'45钢'))]:
    try: print(f.__name__,f(*args))
    except Exception as e: print('ERR',f.__name__,e)
