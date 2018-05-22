from numpy import inf, sqrt

from gpr.misc.objects import material_params, hyperelastic_params


""" SI Units """


MP_H20 = material_params(EOS='sg', ρ0=1000, cv=950, p0=1e5, γ=4.4, pINF=6e8,
                         b0=1e-4, cα=1e-4, μ=1e-3, Pr=7)

MP_Air = material_params(EOS='sg', ρ0=1.18, cv=721, p0=10100, γ=1.4, pINF=0,
                         b0=1, cα=1, μ=1.85e-5, Pr=0.714)

MP_He = material_params(EOS='sg', ρ0=0.163, cv=3127, p0=10100, γ=1.66,
                        pINF=0, b0=1, cα=1, μ=1.99e-5, Pr=0.688)

MP_Al_SG_SI = material_params(EOS='sg', ρ0=2700, cv=897, p0=1e5, γ=3.4,
                              pINF=21.5e9, b0=3160, τ1=inf)

MP_Al_GR_SI = material_params(EOS='gr', ρ0=2710, cv=900, p0=0,
                              c0=sqrt(6220**2 - 4 / 3 * 3160**2), α=1, β=3.577,
                              γ=2.088, b0=3160, τ1=inf, Tref=300)

MP_Al_P_GR_SI = material_params(EOS='gr', ρ0=2710, cv=900, p0=0,
                                c0=sqrt(6220**2 - 4 / 3 * 3160**2), α=1,
                                β=3.577, γ=2.088, b0=3160, σY=0.4e9, τ1=1,
                                n=100, PLASTIC=True, Tref=300)


""" Other Units """


MP_Air_ND = material_params(EOS='sg', ρ0=1, cv=2.5, p0=1, γ=1.4, pINF=0, b0=1,
                            cα=1, μ=5e-4, Pr=2/3)

MP_Al_GR = material_params(EOS='gr', ρ0=2.71, cv=9e-4, p0=0,
                           c0=sqrt(6.22**2 - 4 / 3 * 3.16**2), α=1, β=3.577,
                           γ=2.088, b0=3.16, τ1=inf, Tref=300)

MP_Cu_GR = material_params(EOS='gr', ρ0=8.9, cv=4e-4, p0=0,
                           c0=sqrt(4.6**2 - 4 / 3 * 2.1**2), α=1, β=3, γ=2,
                           b0=2.1, τ1=inf, Tref=300)
# κ=4e-8,
# cα=8.9*sqrt(4.6**2 - 4/3 * 2.1**2)*sqrt(4e-4/300))

MP_Cu_SMG = material_params(EOS='smg', ρ0=8.9, cv=4e-4, p0=0, c0=3.909,
                            Γ0=1.99, s=1.5, e0=0, b0=2.1, τ1=inf, β=3)

MP_Cu_SMG_P = material_params(EOS='smg', ρ0=8.93, cv=1, p0=0, c0=0.394, Γ0=2,
                              s=1.48, e0=0, b0=0.219, σY=9e-4, τ1=0.1, n=10,
                              PLASTIC=True)

MP_Cu_CC = material_params(EOS='cc', ρ0=8.9, cv=3.93e-4, p0=0, Γ0=2, A=1.4567,
                           B=0.1287, R1=2.99, R2=4.1, b0=2.1, τ1=inf, β=3)

MP_TNT_JWL = material_params(EOS='jwl', ρ0=1.84, cv=8.15e-4, p0=0, Γ0=0.25,
                             A=8.545, B=0.205, R1=4.6, R2=1.35, b0=2.1, τ1=inf,
                             β=3)


""" Alternative EOSs """


HYP_Al = hyperelastic_params(ρ0=2.71, α=1, β=3.577, γ=2.088, cv=9e-4, T0=300,
                             b0=3.16, c0=6.22)

HYP_Cu = hyperelastic_params(ρ0=8.9, α=1, β=3, γ=2, cv=4e-4, T0=300,
                             b0=2.1, c0=4.6)

MP_VAC = material_params(EOS='vac', ρ0=0, cv=0, p0=0)
