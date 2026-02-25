## Copyright by ViiVAI Labs and Studio 2025

## definition of haptic hardware
''' haptic python file 
    ------------------
## updated October 13, 2025
- Cleaned up for IEEE submission

'''
import numpy as np
from itertools import zip_longest
from pythonosc import osc_message_builder
from time import sleep, time
from types import SimpleNamespace

### --- Grid Display database ---
def setupHapticGrid(grid_type, border):
    if grid_type == '8ch_triangle':
        act_index = np.array([0, 1, 2, 3, 4, 5, 6, 7]) # actuator grid mapping (touch act[0] and enter MOTU channel)
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]) # gain set on default actuator grid. must be > len(act)
        act_layout = np.array([(0,0),(border.w/2,0),(border.w,0),
                        (border.w/4,border.h/2),(border.w*3/4,border.h/2),(0,border.h),
                        (border.w/2,border.h),(border.w,border.h)])
        tri_layout = np.array([(act_layout[0],act_layout[3],act_layout[5]),(act_layout[0],act_layout[1],act_layout[3]),
                        (act_layout[1],act_layout[3],act_layout[4]),(act_layout[1],act_layout[2],act_layout[4]),
                        (act_layout[2],act_layout[4],act_layout[7]),(act_layout[3],act_layout[5],act_layout[6]),
                        (act_layout[3],act_layout[4],act_layout[6]),(act_layout[4],act_layout[6],act_layout[7])])
        rect_layout = np.array([])
    
    elif grid_type == '8ch_2x4rectangle':
        act_index = np.array([0, 1, 2, 3, 4, 5, 6, 7])
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        act_layout = np.array([(0,0),(border.w/3,0),(2*border.w/3,0),(border.w,0),
                        (0,border.h),(border.w/3,border.h),(2*border.w/3,border.h),(border.w,border.h)])
        tri_layout = np.array([(act_layout[0],act_layout[4],act_layout[5]),(act_layout[0],act_layout[1],act_layout[5]),
                        (act_layout[1],act_layout[5],act_layout[6]),(act_layout[1],act_layout[2],act_layout[6]),
                        (act_layout[2],act_layout[6],act_layout[7]),(act_layout[2],act_layout[3],act_layout[7])])
        rect_layout = np.array([(act_layout[0],act_layout[1],act_layout[5],act_layout[4]),
                                (act_layout[1],act_layout[2],act_layout[6],act_layout[5]),
                                (act_layout[2],act_layout[3],act_layout[7],act_layout[6])])
        
    
    elif grid_type == '12ch_2x6rectangle':
        # act_index = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 13])
        act_index = np.array([4, 2, 6, 8, 1, 13, 5, 3, 7, 9, 0, 12, 10, 11])
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        act_layout = np.array([(0,0),(border.w/5,0),(2*border.w/5,0),(3*border.w/5,0),(4*border.w/5,0),(border.w,0),
                        (0,border.h),(border.w/5,border.h),(2*border.w/5,border.h),(3*border.w/5,border.h),(4*border.w/5,border.h),(border.w,border.h)])
        tri_layout = np.array([(act_layout[0],act_layout[6],act_layout[7]),(act_layout[0],act_layout[1],act_layout[7]),
                               (act_layout[1],act_layout[7],act_layout[8]),(act_layout[1],act_layout[2],act_layout[8]),
                               (act_layout[2],act_layout[8],act_layout[9]),(act_layout[2],act_layout[3],act_layout[9]),
                               (act_layout[3],act_layout[9],act_layout[10]),(act_layout[3],act_layout[4],act_layout[10]),
                               (act_layout[4],act_layout[10],act_layout[11]),(act_layout[4],act_layout[5],act_layout[11])])
        rect_layout = np.array([(act_layout[0],act_layout[1],act_layout[7],act_layout[6]),
                                (act_layout[1],act_layout[2],act_layout[8],act_layout[7]),
                                (act_layout[2],act_layout[3],act_layout[9],act_layout[8]),
                                (act_layout[3],act_layout[4],act_layout[10],act_layout[9]),
                                (act_layout[4],act_layout[5],act_layout[11],act_layout[10])])

        
    elif grid_type == '6ch_3x2rectangle':  # for CR v1.0 [July 21, 2025] 
        act_index = np.array([0, 1, 2, 3, 4, 5])
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        act_layout = np.array([(0,0),(border.w,0),
                               (0,border.h/2),(border.w,border.h/2),
                               (0,border.h),(border.w,border.h)])
        tri_layout = np.array([(act_layout[0],act_layout[2],act_layout[3]),(act_layout[0],act_layout[1],act_layout[3]),
                               (act_layout[2],act_layout[4],act_layout[5]),(act_layout[2],act_layout[3],act_layout[5])])
        rect_layout = np.array([(act_layout[0],act_layout[1],act_layout[3],act_layout[2]),
                                (act_layout[2],act_layout[3],act_layout[5],act_layout[4])])

    elif grid_type == '4ch_2x2rectangle': 
        act_index = np.array([0, 1, 2, 3])
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        act_layout = np.array([(0,0),(border.w,0),(0,border.h),(border.w,border.h)])
        tri_layout = np.array([(act_layout[0],act_layout[2],act_layout[3]),(act_layout[0],act_layout[1],act_layout[3])])
        # tri_layout = np.array([(act_layout[0],act_layout[1],act_layout[2]),(act_layout[1],act_layout[2],act_layout[3])])
        rect_layout = np.array([(act_layout[0],act_layout[1],act_layout[3],act_layout[2])])

    elif grid_type == '2ch_1x2rectangle': 
        act_index = np.array([0, 1])
        g_index = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        act_layout = np.array([(0,0),(border.w,0)])
        tri_layout = np.array([(act_layout[0],act_layout[1],act_layout[1])])
        rect_layout = np.array([])

    else:
        print('no such haptic grid definition exist. Please recheck your grid description')
        quit()

    return act_index, g_index, act_layout, tri_layout, rect_layout

def setupHapticDictionary(device_type, border = SimpleNamespace(x=0, y=0, w=201, h=201)):
    ''' 
    Set up Haptic device dictionary 
    border is a dull by default. 
    Later in device type, set the default border per device or use user defined.
    Modified: Oct 13, 2025
    '''
    hrange = (0,1)
    port = 'UDP'
    actuator_size = 20
    grid_size = (2,4) # 2 rows and 4 columns

    if device_type == 'GrayPad':
        grid_type = '8ch_2x4rectangle'
        grid_size = (2,4) # 2 rows and 4 columns
        device = 'GrayPad'
        location = 'middle back'
        channels = 8
        actuator_type = np.full(channels, 'VCM')
        if border == SimpleNamespace(x=0, y=0, w=201, h=201): border = SimpleNamespace(x=0, y=0, w=480, h=360)
        act_index, g_index, act_layout, tri_layout, rect_layout = setupHapticGrid(grid_type, border)
        physical_layout = np.array([(0,0), (3,0), (6,0), (9,0), (0,3), (3,3), (6,3), (9,3)])
        physical_layout_dim = 'inch'
    
    elif device_type == '8ch_triangle':
        grid_type = '8ch_triangle'
        grid_size = (2,4)#(3,5) # 3 rows and 5 columns
        device = 'BluePad'
        location = 'upper back'
        channels = 8
        actuator_type = np.full(channels, 'VCM')
        if border == SimpleNamespace(x=0, y=0, w=201, h=201): border = SimpleNamespace(x=0, y=0, w=480, h=360)
        act_index, g_index, act_layout, tri_layout, rect_layout = setupHapticGrid(grid_type, border)
        physical_layout = np.array([(0,0), (3,0), (6,0), (1.5,2.5), (4.5,2.5), (0,5), (3,5), (6,5)])
        physical_layout_dim = 'inch'

    elif device_type == 'CR Milano Vibe':  # for CR v1.0 [July 21, 2025] 
        grid_type = '6ch_3x2rectangle'
        grid_size = (3,2) # 3 rows and 2 columns
        device = 'CR Milano Vibe'
        location = 'lower back, seat'
        channels = 6
        actuator_type = np.full(channels, 'ERM')
        port = 'Serial'
        hrange = (0,999)
        if border == SimpleNamespace(x=0, y=0, w=201, h=201): border = SimpleNamespace(x=0, y=0, w=200, h=360)
        act_index, g_index, act_layout, tri_layout, rect_layout = setupHapticGrid(grid_type, border)
        physical_layout = np.array([(0,0),(8,0),(0,12),(8,12),(0,24),(8,24)])
        physical_layout_dim = 'inch'

    elif device_type == '12ch_2x6rectangle':
        grid_type = '12ch_2x6rectangle'
        grid_size = (2,6) # 2 rows and 6 columns
        device = 'HapticSofa'
        location = 'back, seat'
        if border == SimpleNamespace(x=0, y=0, w=201, h=201): border = SimpleNamespace(x=0, y=0, w=640, h=360)
        channels = 12 ## if using MOTU device then use 14 (ch 11-12 are digital)
        actuator_type = np.full(channels, 'VCM')
        act_index, g_index, act_layout, tri_layout, rect_layout = setupHapticGrid(grid_type, border)
        physical_layout = np.array([])
        physical_layout_dim = ''
    
    elif device_type == '4ch_2x2rectangle': 
        grid_type = '4ch_2x2rectangle'
        grid_size = (2,2) # 2 rows and 2 columns
        device = 'default'
        location = 'default'
        channels = 4
        actuator_type = np.full(channels, 'VCM')
        if border == SimpleNamespace(x=0, y=0, w=201, h=201): border = SimpleNamespace(x=0, y=0, w=100, h=100)
        act_index, g_index, act_layout, tri_layout, rect_layout = setupHapticGrid(grid_type, border)
        physical_layout = np.array([])
        physical_layout_dim = ''


    else:
        print('no such haptic grid definition exist. Please recheck your grid description')
        return

    device_dictionary = {
        'device_type': device_type,     # e.g. 'CR Milano Vibe'
        'grid_type': grid_type,         # e.g. '8ch_triangle'
        'grid_size': grid_size,         # e.g. (2,4) # 2 rows and 4 columns
        'device': device,               # e.g. 'GrayPad' or 'CR Milano Vibe'
        'location': location,           # e.g. 'back, seat'
        'channels': channels,
        'act_index': act_index,
        'g_index': g_index,
        'act_layout': act_layout,
        'tri_layout': tri_layout,
        'rect_layout': rect_layout,
        'physical_layout': physical_layout,
        'physical_layout_dim': physical_layout_dim, # e.g. Inch
        'frame border': border,         # e.g. default: pygame.Rect(0, 0, 200, 200)
        'range': hrange,                # e.g. (0,999), default: (0,1)
        'port': port,                   # e.g. 'Serial', default: 'UDP'
        'actuator_type': actuator_type,  # e.g. 'VCM'
        'actuator_size': actuator_size  # e.g. default: 30
    }

    # tri_layout = device_dictionary['tri_layout']
    return device_dictionary

def setHapticOutput(act, g, act_index):
    '''maps index and gain for grid displays
    -index mapping is working for 12 channel grid. do not change the values or circuitry otherwise 
    determine physical channel mapping again.
    - gain mapping has bugs so keep gains to 1.'''
    mact = [x * y for x, y in zip_longest(act, g, fillvalue=1)] # set gain for act in grid
    # mact = list(map(lambda x, y: x * y, act, g))
    for f in range(len(mact)):
        act[f]=mact[f]
    # print(act)

    # rearange output array
    nact = np.zeros(len(act))
    for i in range(len(act_index)):
        nact[act_index[i]]=act[i]
    act = nact

    return(act)
# if __name__ == "__main__":
#     border = SimpleNamespace(x=350, y=250, w=100, h=200)
#     dd=setupHapticDictionary('GrayPad')
    
#     print("Channel number: ", dd['channels'])

### --- UDP messages ---
def sendUDPparameter(client, F, M):
    # string = f"Freq {F}"
    # msg = osc_message_builder.OscMessageBuilder(address = string)
    msg = osc_message_builder.OscMessageBuilder(address = 'Freq')
    msg.add_arg(f'{F}')
    msg = msg.build()
    client.send(msg)    

    msg = osc_message_builder.OscMessageBuilder(address = 'Mod')
    msg.add_arg(f'{M}')
    msg = msg.build()
    client.send(msg) 

    return msg
    
def sendUDPamplitude(client, a):
    for i in range(len(a)):
        s='A'+str(i)
        msg = osc_message_builder.OscMessageBuilder(address = s)
        msg.add_arg(f'{a[i]:.5f}')
        msg = msg.build()
        client.send(msg) 
    return msg

def sendUDPevents(client, msg):
    msg = osc_message_builder.OscMessageBuilder(address = 'Events')
    msg.add_arg(f'{msg}')
    msg = msg.build()
    client.send(msg)    
    return msg

### --- Barycentric rendering ---
def barycentricLinear(act, act_layout, tri_layout, player_dpos):#x, y):
    for i in range(len(act)):
        act[i]=0

    ## determine the triangle inscribing the circle and calculate barycentric coordinate
    for i in tri_layout:
        result, a, b, c = isInsideTriangle(i[0],i[1],i[2], player_dpos)#[x, y])
        
        if result == "Inside":
            break
    # print(i[0],i[1],i[2], a, b, c, result)

    ## set barycenters to act levels
    if result == "Inside":
        for j in range(0,3):
            dd=np.where(np.all(act_layout == i[j], axis=1))
            if   j == 0: act[dd[0]]=a
            elif j == 1: act[dd[0]]=b
            elif j == 2: act[dd[0]]=c
    else:
        print(f"point {player_dpos} is {result} in the triangular grid")
        # print(f"",i[0],i[1],i[2], a, b, c, result)
    return result, act

def barycentricSquare(act, act_layout, tri_layout, player_dpos):#x, y):
    for i in range(len(act)):
        act[i]=0
    
    ## determine the triangle inscribing the circle and calculate barycentric coordinate
    for i in tri_layout:
        result, a, b, c = isInsideTriangle(i[0],i[1],i[2], player_dpos)#[x, y])
        if result == "Inside":
            break
    # print(i[0],i[1],i[2], a, b, c, result)

    ## set barycenters to act levels
    if result == "Inside":
        for j in range(0,3):
            dd=np.where(np.all(act_layout == i[j], axis=1))
            if j == 0: act[dd[0]]=a**2
            elif j == 1: act[dd[0]]=b**2
            elif j == 2: act[dd[0]]=c**2

    return result, act

def barycentricEnergy(act, act_layout, tri_layout, player_dpos):#x, y):
    for i in range(len(act)):
        act[i]=0

    ## determine the triangle inscribing the circle and calculate barycentric coordinate
    for i in tri_layout:
        result, a, b, c = isInsideTriangle(i[0],i[1],i[2], player_dpos)#[x, y])
        if result == "Inside":
            break

    ## set barycenters to act levels
    if result == "Inside":
        for j in range(0,3):
            dd=np.where(np.all(act_layout == i[j], axis=1))
            if j == 0: act[dd[0]]=a**0.5
            elif j == 1: act[dd[0]]=b**0.5
            elif j == 2: act[dd[0]]=c**0.5

    return result, act

def isInsideTriangle_old(A, B, C, P):
    ''' THIS CODE IS DEMOTED DUE TO ERRORS AT X=0 or Y=0. 
    This could be due to floating point miscalulations. 
    '''
    # Calculate the barycentric coordinates of point P with respect to triangle ABC
    denominator = ((B[1] - C[1]) * (A[0] - C[0]) +
				(C[0] - B[0]) * (A[1] - C[1]))
    
    if denominator == 0:
        raise ValueError("The triangle vertices are collinear, cannot calculate barycentric coordinates.")
    
    a = ((B[1] - C[1]) * (P[0] - C[0]) +
		(C[0] - B[0]) * (P[1] - C[1])) / denominator
    b = ((C[1] - A[1]) * (P[0] - C[0]) +
		(A[0] - C[0]) * (P[1] - C[1])) / denominator
    c = 1 - a - b

    # Check if all barycentric coordinates are non-negative
    if a >= 0 and b >= 0 and c >= 0:
        return "Inside", a, b, c
    else:
        return "Outside", a, b, c

def isInsideTriangle(A, B, C, P):
    """
    Calculates the barycentric coordinates of point p relative to triangle abc.
    Args:
        p (tuple): (x, y) coordinates of the point.
        a (tuple): (x1, y1) coordinates of vertex A.
        b (tuple): (x2, y2) coordinates of vertex B.
        c (tuple): (x3, y3) coordinates of vertex C.
    Returns:
        tuple: (u, v, w) barycentric coordinates.
    """
    # Convert tuples to numpy arrays for easier vector operations
    p = np.array(P)
    a = np.array(A)
    b = np.array(B)
    c = np.array(C)

    # Calculate vectors
    v0 = c - a
    v1 = b - a
    v2 = p - a

    # Calculate dot products
    dot00 = np.dot(v0, v0)
    dot01 = np.dot(v0, v1)
    dot02 = np.dot(v0, v2)
    dot11 = np.dot(v1, v1)
    dot12 = np.dot(v1, v2)

    # Calculate denominator
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    if inv_denom == 0:
        raise ValueError("The triangle vertices are collinear, cannot calculate barycentric coordinates.")

    # Calculate barycentric coordinates
    w = (dot11 * dot02 - dot01 * dot12) * inv_denom ## replaced it with v from ai gen code
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom
    u = 1.0 - v - w

    # Check if all barycentric coordinates are non-negative
    if u >= 0 and v >= 0 and w >= 0:
        return "Inside", u, v, w
    else:
        return "Outside", u, v, w

### --- Bilinear interpolation ---
def bilinearLinear(act, act_layout, rect_layout, player_dpos):#x, y):
    for i in range(len(act)):
        act[i]=0

    ## determine the triangle inscribing the circle and calculate barycentric coordinate
    for i in rect_layout:
        result, a, b, c, d = isInsideRectangle(i[0],i[1],i[2],i[3], player_dpos)#[x, y])
        if result == "Inside":
            break
    # print(i[0],i[1],i[2], i[3], a, b, c, d, result)

    ## set barycenters to act levels
    if result == "Inside":
        for j in range(0,4):
            dd=np.where(np.all(act_layout == i[j], axis=1))
            if   j == 0: act[dd[0]]=a
            elif j == 1: act[dd[0]]=b
            elif j == 2: act[dd[0]]=c
            elif j == 3: act[dd[0]]=d

    return result, act

def bilinearEnergy(act, act_layout, rect_layout, player_dpos):#x, y):
    for i in range(len(act)):
        act[i]=0

    ## determine the triangle inscribing the circle and calculate barycentric coordinate
    for i in rect_layout:
        result, a, b, c, d = isInsideRectangle(i[0],i[1],i[2],i[3], player_dpos)#[x, y])
        if result == "Inside":
            break
    # print(i[0],i[1],i[2], i[3], a, b, c, d, result)

    ## set barycenters to act levels
    if result == "Inside":
        for j in range(0,4):
            dd=np.where(np.all(act_layout == i[j], axis=1))
            if   j == 0: act[dd[0]]=a**0.5
            elif j == 1: act[dd[0]]=b**0.5
            elif j == 2: act[dd[0]]=c**0.5
            elif j == 3: act[dd[0]]=d**0.5

    return result, act


def isInsideRectangle(A, B, C, D, P):
    '''
    Calculates the bilinear coordinates and weights at the vertices of an axis-aligned rectangle.

    Args:
        P (tuple): (x, y) coordinates of the point.
        A (tuple): (x1, y1) coordinates of the top-left corner of the rectangle.
        C (tuple): (x2, y) coordinates of the top-right corner of the rectangle.
        B (tuple): (x2, y1) and D (tuple): (x1, y2) are not used.

    Returns:
        dict: A dictionary containing 'u', 'v' (bilinear coordinates) and 'weights'
              (weights at BL, BR, TL, TR vertices).
              Returns None if the point is outside the rectangle.
    '''
    px, py = P
    x1, y1 = A
    x2, y2 = C

    # Calculate bilinear coordinates
    u = (px - x1) / (x2 - x1)
    v = (py - y1) / (y2 - y1)

    # Calculate weights at vertices
    a = (1 - u) * (1 - v) # weight_A
    b = u * (1 - v) # weight_B
    c = (1 - u) * v # weight_C
    d = u * v # weight_D

	# Check if all barycentric coordinates are non-negative
    if (a>=0) and (b>=0) and (c>=0) and (d>=0):
        return "Inside", a, b, d, c ## changed the order from ai gen code
    else:
        return "Outside", a, b, d, c ## replaced it with v from ai gen code


# # A = (0, 0)
# # B = (100,0)
# # C = (100,100)
# # D = (0, 100)
# # test_point_inside = (0, 20)
# # test_point_outside = (0, 169)

# # A = (67, 0)
# # C = (134, 201)
# # B, D = (0,0), (0,0) ## not used
# # print(f"Bilinear weights for {test_point_inside}: {isInsideRectangle(A, B, C, D, test_point_inside)}")
# # print(f"Bilinear weights for {test_point_outside}: {isInsideRectangle(A, B, C, D, test_point_outside)}")



### --- linearhaptic rendering ---
def map_linearhaptics(value, minH, maxH, minI=0.0, maxI=1.0):
    ''' this function maps linear HDT function
    added July 30th '''
    return minH + ((value-minI)*(maxH - minH)/(maxI - minI))

# print(map_linearhaptics(20, 0, 1, 0, 999))


# Example usage:

# ## test bilinear interpolation in a rectangle
# dd=setupHapticDictionary('GrayPad')
# rect_layout=dd['rect_layout']
# act_layout=dd['act_layout']
# tri_layout=dd['tri_layout']
# channels = dd['channels']
# # print("Rect Layout", rect_layout)
# # print("Actuator Layout", act_layout)
# test_point_inside = (13, 50)
# test_point_outside = (20, 0)
# act=np.zeros(channels)

# print(f"Bilinear amps for {test_point_inside}: {bilinearLinear(act, act_layout, rect_layout, test_point_inside)} -- sum: {np.sum(act)}")
# print(f"Bilinear amps for {test_point_outside}: {bilinearLinear(act, act_layout, rect_layout, test_point_outside)} -- sum: {np.sum(act)}")

# print(f"Barycentric amps for {test_point_inside}: {barycentricEnergy(act, act_layout, tri_layout, test_point_inside)} -- sum: {np.sum(act)}")
# print(f"Barycentric amps for {test_point_outside}: {barycentricEnergy(act, act_layout, tri_layout, test_point_outside)} -- sum: {np.sum(act)}")
