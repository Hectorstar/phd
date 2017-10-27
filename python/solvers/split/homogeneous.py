from itertools import product

from numpy import dot, tensordot, zeros

from solvers.basis import derivative_values
from system.system import Bdot, flux, system
from options import nV, dx, dy, N1, ndim


DERIVS = derivative_values()


def derivative(X, dim):
    """ Returns the derivative of polynomial coefficients X with respect to
        dimension dim. X can be of shape (N1,...) or (N1,N1,...)
    """
    if dim==0:
        return tensordot(DERIVS, X, (1,0)) / dx
    elif dim==1:
        return tensordot(DERIVS, X, (1,1)).swapaxes(0,1) / dy

def weno_midstepper(wh, dt, PAR):
    """ Steps the WENO reconstruction forwards by dt/2, under the homogeneous system
    """
    USE_JACOBIAN = 0

    nx,ny,nz = wh.shape[:3]

    F = zeros([N1]*ndim + [nV])
    G = zeros([N1]*ndim + [nV])
    Bdwdx = zeros(nV)
    Bdwdy = zeros(nV)

    for i,j,k in product(range(nx), range(ny), range(nz)):

        w = wh[i,j,k]
        dwdx = derivative(w, 0)

        if ndim==1:

            if USE_JACOBIAN:
                for a in range(N1):
                    Mx = system(w[a], 0, PAR)
                    w[a] -= dt/2 * dot(Mx, dwdx[a])
            else:
                for a in range(N1):
                    F[a] = flux(w[a], 0, PAR)
                dFdx = derivative(F, 0)
                for a in range(N1):
                    Bdot(Bdwdx, dwdx[a], w[a], 0)
                    w[a] -= dt/2 * (dFdx[a] + Bdwdx)

        elif ndim==2:

            dwdy = derivative(w, 1)

            if USE_JACOBIAN:
                for a,b in product(range(N1), range(N1)):
                    Mx = system(w[a,b], 0, PAR)
                    My = system(w[a,b], 1, PAR)
                    w[a,b] -= dt/2 * (dot(Mx, dwdx[a,b]) + dot(My, dwdy[a,b]))
            else:
                for a,b in product(range(N1), range(N1)):
                    F[a,b] = flux(w[a,b], 0, PAR)
                    G[a,b] = flux(w[a,b], 1, PAR)
                dFdx = derivative(F, 0)
                dGdy = derivative(G, 1)
                for a,b in product(range(N1), range(N1)):
                    Bdot(Bdwdx, dwdx[a,b], w[a,b], 0)
                    Bdot(Bdwdy, dwdy[a,b], w[a,b], 1)
                    w[a,b] -= dt/2 * (dFdx[a,b] + dGdy[a,b] + Bdwdx + Bdwdy)
