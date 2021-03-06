import GPRpy

from numpy import array, dot, int32, ones, prod, zeros

from ader.fv.fluxes import B_INT, D_OSH, D_ROE, D_RUS
from ader.fv.fv import endpoints

from gpr.misc.structures import State
from gpr.sys.eigenvalues import Xi1, Xi2

from bindings_tests.test_functions import check, generate_vector


convert_fluxes = {D_RUS: 0,
                  D_ROE: 1,
                  D_OSH: 2}


""" FLUXES """


def TAT_test(d, MP):

    Q = generate_vector(MP)
    P = State(Q, MP)

    Ξ1 = Xi1(P, d, MP)
    Ξ2 = Xi2(P, d, MP)
    TAT_py = dot(Ξ1, Ξ2)
    TAT_cp = GPRpy.system.thermo_acoustic_tensor(Q, d, MP)

    print("TAT   ", check(TAT_cp, TAT_py))
    return TAT_cp, TAT_py


def Bint_test(d, fvSolver):

    MP = fvSolver.pars

    Q1 = generate_vector(MP)
    Q2 = generate_vector(MP)

    Bint_cp = GPRpy.solvers.fv.Bint(Q1, Q2, d, MP)
    Bint_py = B_INT(fvSolver, Q1, Q2, d)

    print("Bint  ", check(Bint_cp, Bint_py))
    return Bint_cp, Bint_py


def D_RUS_test(d, fvSolver):

    MP = fvSolver.pars

    Q1 = generate_vector(MP)
    Q2 = generate_vector(MP)

    D_RUS_cp = GPRpy.solvers.fv.D_RUS(Q1, Q2, d, MP)
    D_RUS_py = D_RUS(fvSolver, Q1, Q2, d,)

    print("D_RUS ", check(D_RUS_cp, D_RUS_py))
    return D_RUS_cp, D_RUS_py


def D_ROE_test(d, fvSolver):

    MP = fvSolver.pars

    Q1 = generate_vector(MP)
    Q2 = generate_vector(MP)

    D_ROE_cp = GPRpy.solvers.fv.D_ROE(Q1, Q2, d, MP)
    D_ROE_py = D_ROE(fvSolver, Q1, Q2, d)

    print("D_ROE ", check(D_ROE_cp, D_ROE_py))
    return D_ROE_cp, D_ROE_py


def D_OSH_test(d, fvSolver):

    MP = fvSolver.pars

    Q1 = generate_vector(MP)
    Q2 = generate_vector(MP)

    D_OSH_cp = GPRpy.solvers.fv.D_OSH(Q1, Q2, d, MP)
    D_OSH_py = D_OSH(fvSolver, Q1, Q2, d)

    print("D_OSH ", check(D_OSH_cp, D_OSH_py))
    return D_OSH_cp, D_OSH_py


""" FINITE VOLUME (NDIM=1) """


def FVc_test(qh_py, dX, dt, fvSolver):

    SOURCES = fvSolver.S is not None
    TIME = fvSolver.time_rec
    NV = fvSolver.NV
    NDIM = fvSolver.NDIM
    MP = fvSolver.pars
    mask = None

    if not SOURCES:
        shape = qh_py.shape
        newShape = shape[:NDIM] + (1,) + shape[NDIM:]
        qh_py = qh_py.reshape(newShape)

    nX = array(qh_py.shape[:NDIM])
    ncell = prod(nX)
    mask = ones(ncell, dtype=bool)

    FVc_py = zeros(list(nX - 2) + [NV])
    FVc_cp = zeros(FVc_py.size)

    if NDIM == 1:
        GPRpy.solvers.fv.centers1(FVc_cp, qh_py.ravel(), nX[0] - 2, dt, dX[0],
                                  SOURCES, TIME, MP, mask)

    elif NDIM == 2:
        GPRpy.solvers.fv.centers2(FVc_cp, qh_py.ravel(), nX[0] - 2, nX[1] - 2, dt,
                                  dX[0], dX[1], SOURCES, TIME, MP, mask)

    fvSolver.centers(FVc_py, qh_py, dX, mask)
    FVc_py *= dt

    FVc_cp = FVc_cp.reshape(FVc_py.shape)
    print("FVc   ", check(FVc_cp, FVc_py))
    return FVc_cp, FVc_py


def FVi_test(qh_py, dX, dt, fvSolver):

    SOURCES = fvSolver.S is not None
    TIME = fvSolver.time_rec
    NV = fvSolver.NV
    NDIM = fvSolver.NDIM
    MP = fvSolver.pars
    FLUX = convert_fluxes[fvSolver.D_FUN]
    ENDVALS = fvSolver.ENDVALS
    mask = None

    if not SOURCES:
        shape = qh_py.shape
        newShape = shape[:NDIM] + (1,) + shape[NDIM:]
        qh_py = qh_py.reshape(newShape)

    qEnd = endpoints(qh_py, NDIM, ENDVALS)

    nX = array(qh_py.shape[:NDIM])
    ncell = prod(nX)
    mask = ones(ncell, dtype=bool)

    FVi_py = zeros(list(nX - 2) + [NV])
    FVi_cp = zeros(FVi_py.size)

    if NDIM == 1:
        GPRpy.solvers.fv.interfs1(FVi_cp, qh_py.ravel(), nX[0] - 2, dt, dX[0],
                                  TIME, FLUX, MP, mask)

    elif NDIM == 2:
        GPRpy.solvers.fv.interfs2(FVi_cp, qh_py.ravel(), nX[0] - 2, nX[1] - 2,
                                  dt, dX[0], dX[1], TIME, FLUX, MP, mask)

    fvSolver.interfaces(FVi_py, qEnd, dX, mask)
    FVi_py *= dt

    FVi_cp = FVi_cp.reshape(FVi_py.shape)
    print("FVi   ", check(FVi_cp, FVi_py))
    return FVi_cp, FVi_py


def FV_test(qh_py, dX, dt, fvSolver):

    SOURCES = fvSolver.S is not None
    TIME = fvSolver.time_rec
    FLUX = convert_fluxes[fvSolver.D_FUN]
    NDIM = fvSolver.NDIM
    MP = fvSolver.pars

    nX = array(qh_py.shape[:NDIM], dtype=int32)
    ncell = prod(nX)
    mask = ones(ncell, dtype=bool)

    FV_py = fvSolver.solve(qh_py, dt, dX)

    FV_cp = zeros(FV_py.size)
    GPRpy.solvers.fv.fv_launcher(FV_cp, qh_py.ravel(), nX - 2, dt, array(dX),
                                 SOURCES, TIME, FLUX, MP, mask)

    FV_cp = FV_cp.reshape(FV_py.shape)
    print("FV    ", check(FV_cp, FV_py))
    return FV_cp, FV_py
