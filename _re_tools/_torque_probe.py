import sys; sys.path.insert(0,'.')
import torque_data as t
print('sizes', list(t.SIZES.items())[:3])
print('grades', list(t.GRADES.items())[:3])
print('coef', t.TORQUE_COEFFICIENT)
for args in [('hex','M10','8.8'),('socket','M10','8.8'),('hex','M12','10.9')]:
    try: print(args,t.get_torque(*args))
    except Exception as e: print('ERR',args,e)
print('estimate',t.estimate_torque('8.8',10,0.2))
