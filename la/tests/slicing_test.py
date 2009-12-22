"""Notes on slicing, converted to test

"""

''' 
indexing with nd boolean array fails
>>> lar[lar>0]
Traceback (most recent call last):
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 722, in __getitem__
    raise IndexError, msg
IndexError: Only slice, integer, and seq (list, tuple, 1d array) indexing supported
lar.x[lar.x>0]  # this works but creates 1d array, only useful for changes


indexing with 1d boolean array fails
>>> la1_3d[lar.x[:,0,0]>0,:,:]
Traceback (most recent call last):
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 725, in __getitem__
    return type(self)(x, label)
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 60, in __init__
    raise ValueError, msg2 % (i, value, key)
ValueError: Elements of label not unique along dimension 0. There are 2 labels named `1`.
>>> lar.x[lar.x[:,0,0]>0,:,:] # this works


#list slicing fails
>>> lar.x[[0,1], [0,1], [0,1]]
array([ 2.,  4.])
>>> lar[[0,1], [0,1], [0,1]]
Traceback (most recent call last):
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 725, in __getitem__
    return type(self)(x, label)
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 50, in __init__
    if x.shape[i] != nlabel:
IndexError: tuple index out of range


broadcasting of slices fails in larry
>>> lar.x[(np.array([0,1])[:,None], [0,1], [0,1])]
array([[ 2.,  2.],
       [ 4.,  4.]])
>>> lar[(np.array([0,1])[:,None], [0,1], [0,1])]
Traceback (most recent call last):
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 725, in __getitem__
    return type(self)(x, label)
  File "c:\josef\eclipsegworkspace\larry\trunk\la\deflarry.py", line 50, in __init__
    if x.shape[i] != nlabel:
IndexError: tuple index out of range
'''
import numpy as np
from numpy.testing import assert_
import la
#from deflarry_test import nocopy doesn't work for unequal shapes
#helper function to check reference for slices ?
nan = np.nan

def getnplabel3d(idx, slices, reduced=False): #True):
    '''constructs list of labels for comparison with generic larry
    
    does not preserve ordering of labels in each axis 
    '''
    ndim = idx[0].ndim
    labs = [np.unique(idx[ii][slices]).tolist() for ii in range(ndim)]
    if reduced:
        labs = [ii for ii in labs if len(ii) > 1]
    return labs

def getnplabel3dm(idx, slices, reduced=True):
    '''constructs list of labels for comparison with generic larry
    
    preserves ordering of labels in each axis, usable for morph comparison
    '''
    #not sure anymore if it doesn't work easier
    ndim = idx[0].ndim
    labs = []
    for ii in range(ndim):
        sliceidx = list(np.zeros(ndim,int))
        sliceidx[ii] = slices[ii]
        labs.append((idx[ii][sliceidx]).tolist())
    if reduced:
        labs = [ii for ii in labs if len(ii) > 1]
    return labs

# larry definition on module level or in class setup, for now only 1 larry used 

x1 = np.array([[ 2.0, 2.0, 3.0, 1.0],
               [ 3.0, 2.0, 2.0, 1.0],
               [ 1.0, 1.0, 1.0, 1.0]])
#The next array with nan fails because comparison in test does not
#handle nans correctly, fixed in numpy 1.4 for array_equal, not ==
#results for slicing are independent of nans, so skip nans
x1nan = np.array([[ 2.0, 2.0, nan, 1.0],
               [ 3.0, nan, 2.0, 1.0],
               [ 1.0, 1.0, 1.0, 1.0]])

# slice tests for 3d

la1_2d0 = la.larry(x1)
la1_2d1 = la.larry(x1)
x1_3d = np.rollaxis(np.dstack([x1,2*x1]),2)
la1_3d = la.larry(x1_3d)
n0,n1,n2 = la1_3d.shape
idx = np.mgrid[0:n0,0:n1,0:n2]
          
        
def test_slicing():
    slices = (slice(None), slice(None), slice(None,2))
    larli = [la1_3d, la1_2d0]
    sliceli = [(slice(None), slice(None), slice(None,2)),
               (slice(None), slice(None,1), slice(None,2)),
               (slice(None,1), slice(None), slice(None,2)),
               (slice(None), slice(None), slice(2)),
               (slice(None), slice(None), 0),
               (slice(None), 0, 0),
               (slice(None), slice(2)),
               #([0,1], [0,1], [0,1]),  # fails in larry
               #(np.array([0,1])[:,None], [0,1], [0,1]), #broadcasting
               (0,0,0)
               ]
    
    for lar in larli:
        for slices in sliceli:
            ndim = lar.ndim
            #print lar.shape
            #print slices
            # create arrays corresponding to labels for slicing
            idxslice = [slice(0,nn) for nn in lar.shape]
            idx = np.mgrid[idxslice]
            slices = slices[:ndim]  # to run same loop on 2d and 3d
            lasliced = lar[slices]
            if not np.isscalar(lasliced):
                lasliced_x = lasliced.x
                lasliced_label = lasliced.label
            else:
                lasliced_x = lasliced
                lasliced_label = []
            reduced = np.ndim(lar.x) > np.ndim(lasliced_x)
            
            newlabels = getnplabel3d(idx, slices, reduced=reduced)
            yield assert_, np.all(lasliced_x == lar.x[slices]), \
                    'slicing\n%s\n%s' % (repr(lasliced_x), repr(lar.x[slices]))
            yield assert_, lasliced_label == newlabels,\
                    'slicing\n%s\n%s' % (repr(lasliced_label),
                    repr(newlabels))
    

########## add morphing


def test_morph():
    larli = [la1_3d, la1_2d0]
    slicesmorph = [([0,2,1,3], -1),
                   ([0,2,1], 2),
                   ([1,0], 0),
                   ([0,2,1], 1)
                   ]

    #some of the things in the following loop are not necessary because
    #morph doesn't reduce dimension
    for lar in larli: 
        for newlab, axis in slicesmorph:
            ndim = lar.ndim
            if axis > (ndim - 1):
                #print 'infeasible dimension'
                continue  # skip infeasible cases
            
            slices = [slice(None)]*ndim
            slices[axis] = newlab
            #print lar.shape
            #print slices
            
            # create arrays corresponding to labels for slicing
            idxslice = [slice(0,nn) for nn in lar.shape]
            idx = np.mgrid[idxslice]
            slices = slices[:ndim]  # to run same loop on 2d and 3d
            lasliced = lar.morph(newlab, axis)
            if not np.isscalar(lasliced):
                lasliced_x = lasliced.x
                lasliced_label = lasliced.label
            else:
                lasliced_x = lasliced
                lasliced_label = []
            reduced = np.ndim(lar.x) > np.ndim(lasliced_x)
            
            newlabels = getnplabel3dm(idx, slices, reduced=reduced)
#            print lasliced_x
#            print lar.x[slices]
#            print lasliced_label
#            print newlabels
            yield assert_, np.all(lasliced_x == lar.x[slices]), \
                    'slicing\n%s\n%s' % (repr(lasliced_x), repr(lar.x[slices]))
            yield assert_, lasliced_label == newlabels,\
                    'slicing\n%s\n%s' % (repr(lasliced_label),
                    repr(newlabels))


