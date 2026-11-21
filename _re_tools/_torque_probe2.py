import sys; sys.path.insert(0,'.')
import torque_data as t
print('hex M10',t.HEX_BOLT.get('M10'))
print('socket M10',t.SOCKET_CAP.get('M10'))
print('self M4',list(t.SELF_TAPPING.items())[:2])
print('grades socket',t.GRADES)
print('sizes self',t.SIZES)
print('coef',t.TORQUE_COEFFICIENT)
