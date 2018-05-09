from numpy import amax, array, column_stack, concatenate, dot, eye, zeros
from scipy.linalg import inv, solve

from gpr.misc.functions import reorder
from gpr.misc.structures import State
from gpr.opts import THERMAL
from gpr.sys.analytical import ode_solver_cons
from gpr.sys.eigenvalues import Xi1, Xi2
from gpr.sys.eigenvectors import eigen, decompose_Ξ, get_indexes
from gpr.vars.eos import total_energy
from gpr.vars.wavespeeds import c_0


RELAXATION = True
STAR_TOL = 1e-6


n1, n2, n3, n4, n5 = get_indexes()


def Pvec(P):
    """ Vector of primitive variables
        NOTE: Uses atypical ordering
    """
    if THERMAL:
        ret = zeros(17)
        ret[14:17] = P.J
    else:
        ret = zeros(14)

    ret[0] = P.ρ
    ret[1] = P.p()
    ret[2:11] = P.A.ravel(order='F')
    ret[11:14] = P.v

    return ret


def Pvec_to_Cvec(P, MP):
    """ Returns the vector of conserved variables, given the vector of
        primitive variables
    """
    Q = P.copy()
    ρ = P[0]
    A = P[5:14].reshape([3, 3])

    λ = 0

    Q[1] = ρ * total_energy(ρ, P[1], P[2:5], A, P[14:17], λ, MP)
    Q[2:5] *= ρ
    Q[14:] *= ρ

    return Q


def check_star_convergence(QL_, QR_, MPL, MPR):

    PL_ = State(QL_, MPL)
    PR_ = State(QR_, MPR)

    cond1 = amax(abs(PL_.Σ()[0] - PR_.Σ()[0])) < STAR_TOL

    if THERMAL:
        cond2 = abs(PL_.T() - PR_.T()) < STAR_TOL
    else:
        cond2 = True

    return cond1 and cond2


def left_riemann_constraints(P, Lhat, sgn):

    σρ = P.dσdρ()
    σA = P.dσdA()

    Lhat[:3, 0] = -σρ[0]
    Lhat[:3, 1] = array([1, 0, 0])
    for i in range(3):
        Lhat[:3, 2 + 3 * i:5 + 3 * i] = -σA[0, :, :, i]
    Lhat[:3, 11:] = 0

    if THERMAL:
        Lhat[3, 0] = P.dTdρ()
        Lhat[3, 1] = P.dTdp()
        Lhat[3, 2:] = 0

    Lhat[n1:n2, 11:n5] *= -sgn

    return Lhat


def riemann_constraints(P, sgn, MP, left=False):
    """ K=R: sgn = -1
        K=L: sgn = 1
        NOTE: Uses atypical ordering

        Extra constraints are:
        dΣ = dΣ/dρ * dρ + dΣ/dp * dp + dΣ/dA * dA
        dT = dT/dρ * dρ + dT/dp * dp
        v*L = v*R
        J*L = J*R
    """
    _, Lhat, Rhat = eigen(P, 0, False, MP, values=False, right=True, left=left,
                          typical_order=False)

    if left:
        Lhat = left_riemann_constraints(P, Lhat, sgn)

    ρ = P.ρ
    A = P.A
    σρ = P.dσdρ()
    σA = P.dσdA()

    e0 = array([1, 0, 0])
    Π1 = σA[0, :, :, 0]

    tmp = zeros([5, 5])
    tmp[:3, 0] = -σρ[0]
    tmp[0, 1] = 1
    tmp[:3, 2:5] = -Π1

    if THERMAL:

        tmp[3, 0] = P.dTdρ()
        tmp[3, 1] = P.dTdp()
        tmp[4, 0] = -1 / ρ
        tmp[4, 2:5] = inv(A)[0]

    else:

        p = P.p()
        σ = P.σ()
        c0 = c_0(ρ, p, A, MP)

        B = zeros([2, 3])
        B[0, 0] = ρ
        B[1] = σ[0] - ρ * σρ[0]
        B[1, 0] += ρ * c0**2

        rhs = column_stack((-σρ[0], e0))
        C = solve(Π1, rhs)

        BA_1 = dot(B, inv(A))
        Z = eye(2) - dot(BA_1, C)
        W = concatenate([eye(2), -BA_1], axis=1)
        tmp[3:5] = solve(Z, W)

    b = zeros([5, n1])
    b[:n1, :n1] = eye(n1)
    X = solve(tmp, b)

    Rhat[:5, :n1] = X

    Ξ1 = Xi1(P, 0, MP)
    Ξ2 = Xi2(P, 0, MP)
    Q, Q_1, _, D_1 = decompose_Ξ(Ξ1, Ξ2)
    Y0 = dot(Q_1, dot(D_1, Q))

    Rhat[11:n5, :n1] = -sgn * dot(Y0, dot(Ξ1, X))
    Rhat[:11, n1:n2] = 0
    Rhat[11:n5, n1:n2] = sgn * dot(Q_1, D_1)

    return Lhat, Rhat


def star_stepper(QL, QR, MPL, MPR, STICK=True):

    PL = State(QL, MPL)
    PR = State(QR, MPR)

    _, RL = riemann_constraints(PL, 1, MPL)
    _, RR = riemann_constraints(PR, -1, MPR)

    if STICK:

        YL = RL[11:n5, :n1]
        YR = RR[11:n5, :n1]

        if THERMAL:
            xL = concatenate([PL.Σ()[0], [PL.T()]])
            xR = concatenate([PR.Σ()[0], [PR.T()]])
            yL = concatenate([PL.v, PL.J[:1]])
            yR = concatenate([PR.v, PR.J[:1]])
        else:
            xL = PL.Σ()[0]
            xR = PR.Σ()[0]
            yL = PL.v
            yR = PR.v

        x_ = solve(YL - YR, yR - yL + dot(YL, xL) - dot(YR, xR))

    else:  # slip conditions - only implemented for non-thermal

        if THERMAL:
            YL = RL[[11, 14], :n1]
            YR = RR[[11, 14], :n1]

            xL = array([PL.Σ()[0], PL.T()])
            xR = array([PR.Σ()[0], PR.T()])
            yL = array([PL.v[0], PL.J[0]])
            yR = array([PR.v[0], PR.J[0]])

            M = YL[:, [0, -1]] - YR[:, [0, -1]]
            x_ = solve(M, yR - yL + dot(YL, xL) - dot(YR, xR))
            x_ = array([x_[0], 0, 0, x_[1]])

        else:
            YL = RL[11, :n1]
            YR = RR[11, :n1]

            xL = PL.Σ()[0]
            xR = PR.Σ()[0]
            yL = PL.v[0]
            yR = PR.v[0]

            x_ = (yR - yL + dot(YL, xL) - dot(YR, xR)) / (YL - YR)[0]
            x_ = array([x_, 0, 0])

    cL = zeros(n5)
    cR = zeros(n5)
    cL[:n1] = x_ - xL
    cR[:n1] = x_ - xR

    PLvec = Pvec(PL)
    PRvec = Pvec(PR)
    PL_vec = dot(RL, cL) + PLvec
    PR_vec = dot(RR, cR) + PRvec
    QL_ = Pvec_to_Cvec(reorder(PL_vec), MPL)
    QR_ = Pvec_to_Cvec(reorder(PR_vec), MPR)

    return QL_, QR_


def rotate_tensors(Q, R):

    Q[2:5] = dot(R, Q[2:5])

    A = Q[5:14].reshape([3,3])
    A_ = dot(R, dot(A, R.T))
    Q[5:14] = A_.ravel()

    if THERMAL:
        Q[14:17] = dot(R, Q[14:17])


def star_states(QL, QR, MPL, MPR, dt, R):

    QL_ = QL[:n5].copy()
    QR_ = QR[:n5].copy()

    rotate_tensors(QL_, R)
    rotate_tensors(QR_, R)

    while not check_star_convergence(QL_, QR_, MPL, MPR):

        if RELAXATION:
            ode_solver_cons(QL_, dt / 2, MPL)
            ode_solver_cons(QR_, dt / 2, MPR)

        QL_, QR_ = star_stepper(QL_, QR_, MPL, MPR)

    rotate_tensors(QL_, R.T)
    rotate_tensors(QR_, R.T)

    retL = QL.copy()
    retR = QR.copy()
    retL[:n5] = QL_
    retR[:n5] = QR_

    return retL, retR
