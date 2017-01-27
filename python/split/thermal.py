from numpy import exp, eye, sqrt

from auxiliary.funcs import L2_1D
from gpr.variables.eos import E_2A, E_3, E_J, energy_to_temperature
from gpr.variables.material_functions import theta_2


def f_J(ρ, E, A, J, PAR):
    T = energy_to_temperature(E, A, J, PAR)
    return - E_J(J, PAR.α2) / theta_2(ρ, T, PAR.ρ0, PAR.T0, PAR.α2, PAR.τ2)

def jac_J(ρ, E, A, J, PAR):
    T = energy_to_temperature(E, A, J, PAR)
    return -(T * PAR.ρ0) / (PAR.T0 * ρ * PAR.τ1) * eye(3)

def solver_thermal_analytic_ideal(ρ, E, A, J, v, dt, PAR):
    """ Solves the thermal impulse ODE analytically in 3D for the ideal gas EOS
    """
    c1 = E - E_2A(A, PAR.cs2) - E_3(v)
    c2 = PAR.α2 / 2
    k = 2 * PAR.ρ0 / (PAR.τ2 * PAR.T0 * ρ * PAR.cv)
    c1 *= k
    c2 *= k

    ea = exp(c1*dt)
    den = ea - c2/c1*(ea-1)*L2_1D(J)
    return J / sqrt(den)