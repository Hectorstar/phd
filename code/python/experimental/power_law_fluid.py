from numpy import diag, dot, eye, trace
from numpy.linalg import norm
from numpy.random import rand
from scipy.integrate import quad


def dev(X):
    return X - trace(X) / 3 * eye(3)


x = rand(3)
X = diag(x)

ρ = x[0] * x[1] * x[2]
m = (x[0] + x[1] + x[2]) / 3
u = ((x[0] - x[1])**2 + (x[1] - x[2])**2 + (x[2] - x[0])**2) / 3

# Second order

I2 = x[0]**2 + x[1]**2 + x[2]**2
I11 = x[0] * x[1] + x[1] * x[2] + x[2] * x[0]

print('m^2: ', m**2 - 1/9 * (I2 + 2*I11))
print('u:   ', u - 2/3 * (I2 - I11))

# Third order

I3 = x[0]**3 + x[1]**3 + x[2]**3
I21 = x[0]**2 * x[1] + x[1]**2 * x[0] + \
      x[1]**2 * x[2] + x[2]**2 * x[1] + \
      x[2]**2 * x[0] + x[0]**2 * x[2]

print('m^3: ', m**3 - 1/27 * (I3 + 3*I21 + 6*ρ))
print('mu:  ', m*u - 2/9 * (I3 - 3*ρ))

# Fourth order

I4 = x[0]**4 + x[1]**4 + x[2]**4
I31 = x[0]**3 * x[1] + x[1]**3 * x[0] + \
      x[1]**3 * x[2] + x[2]**3 * x[1] + \
      x[2]**3 * x[0] + x[0]**3 * x[2]
I22 = x[0]**2 * x[1]**2 + x[1]**2 * x[2]**2 + x[2]**2 * x[0]**2
I211 = x[0]**2 * x[1] * x[2] + x[1]**2 * x[2] * x[0] + x[2]**2 * x[0] * x[1]

print('ρm:  ', ρ*m - 1/3 * I211)
print('m^2u:', m**2*u - 2/27 * (I4 + I31 - 9*ρ*m))
print('m^4: ', m**4 - 1/81 * (I4 + 4*I31 + 6*I22 + 36*ρ*m))
print('u^2: ', u**2 - 4/9 * (I4 - 2*I31 + 3*I22))

n = norm(dot(X, dev(X)))
print('|XdevX|^2:', n**2 - 2/9 * (2 * I4 - 2 * I31 + I22 + 3 * ρ*m))

print(9 * n**2 - (4 * I4 - 4 * I31 + 2 * I22 + 6 * ρ*m))
print(27*m**2*u + 18*ρ*m - (2*I4 + 2*I31))
print(81*m**4 - 36*ρ*m - (I4 + 4*I31 + 6*I22))
print(9*u**2 - (4*I4 - 8*I31 + 12*I22))
print(n**2 - (1/2*u**2 + 4*m**2*u - 6*m**4 + 6*ρ*m))

τ = rand()
a = rand()
b = rand()

m = 1 + exp(-9*τ) / 3 * (a*exp(3*τ) - b)
u = exp(-9*τ) * (2*a*exp(3*τ) - 3*b)

z1 = 1/2*u**2 + 4*m**2*u - 6*m**4 + 6*m
z2 = 1/54 * (108*a*exp(-6*τ) - 324*b*exp(-9*τ) + 180*a**2*exp(-12*τ) \
             - 612*a*b*exp(-15*τ) + 459*b**2*exp(-18*τ) - 24*a**2*b*exp(-21*τ) \
             + (48*a*b**2-4*a**4)*exp(-24*τ) + (16*a**3*b-24*b**3)*exp(-27*τ) \
             - 24*a**2*b**2*exp(-30*τ) + 16*a*b**3*exp(-33*τ) - 4*b**4*exp(-36*τ))

print(z1 - z2)


def f1(τ):
    e_τ = exp(-τ)
    return 108 * a * e_τ**6 - 324 * b * e_τ**9 + 180 * a**2 * e_τ**12 \
           - 612 * a * b * e_τ**15 + 459 * b**2 * e_τ**18 \
           - 24 * a**2 * b * e_τ**21 + (48 * a * b**2 - 4 * a**4) * e_τ**24 \
           + (16 * a**3 * b - 24 * b**3) * e_τ**27 - 24 * a**2 * b**2 * e_τ**30 \
           + 16 * a * b**3 * e_τ**33 - 4 * b**4 * e_τ**36


def f2(τ):
    c = 108 * a - 324 * b + 180 * a**2 - 612 * a * b + 459 * b**2 \
        - 24 * (a**2 * b - 2 * a * b**2 + b**3) - 4 * (a - b)**4
    den = 18 * a - 36 * b + 15 * a**2 - 204 / 5 * a * b + 51 / 2 * b**2 \
          - 8 / 7 * a**2 * b + 2 * a * b**2 - 8 / 9 * b**3 - a**4 / 6 \
          + 16 / 27 * a**3 * b - 4 / 5 * a**2 * b**2 + 16 / 33 * a * b**3 \
          - b**4 / 9
    λ = c / den
    return c * exp(-λ * τ)


print(f1(0) - f2(0))
print(quad(f1, 0, inf)[0] - quad(f2, 0, inf)[0])