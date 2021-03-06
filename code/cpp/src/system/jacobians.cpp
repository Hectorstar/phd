#include "../etc/types.h"
#include "energy/derivatives.h"
#include "energy/mg.h"
#include "functions/matrices.h"
#include "functions/vectors.h"
#include "objects.h"
#include "variables/state.h"
#include "waves/shear.h"

MatV_V dFdP(VecVr Q, int d, Par &MP) {
  // Returns Jacobian of flux vector with respect to the primitive variables
  MatV_V ret = MatV_V::Zero();

  double ρ = Q(0);
  double E = Q(1) / ρ;
  double p = pressure(Q, MP);
  Vec3 v = get_ρv(Q) / ρ;
  Mat3_3Map A = get_A(Q);

  double Eρ = dEdρ(Q, MP);
  double Ep = dEdp(Q, MP);
  double vd = v(d);
  double ρvd = ρ * vd;
  Mat3_3 G = A.transpose() * A;
  Mat3_3 A_devG = AdevG(A);

  ret(0, 0) = vd;
  ret(0, 2 + d) = ρ;
  ret(1, 0) = (E + ρ * Eρ) * vd;
  ret(1, 1) = (ρ * Ep + 1) * vd;
  ret.block<1, 3>(1, 2) = ρ * vd * v;
  ret(1, 2 + d) += ρ * E + p;
  ret.block<3, 1>(2, 0) = vd * v;
  for (int i = 2; i < 5; i++)
    ret(i, i) = ρvd;
  ret.block<3, 1>(2, 2 + d) += ρ * v;
  ret(2 + d, 1) = 1.;

  if (VISCOUS) {
    Vec3 σ = sigma(Q, MP, d);
    Vec3 σρ = dsigmadρ(Q, MP, d);
    Mat3_3 ψ_ = dEdA(Q, MP);

    double cs2 = c_s2(ρ, MP);
    for (int i = 0; i < 3; i++)
      for (int j = 0; j < 3; j++) {
        int ind = i * 3 + j;
        double tmp = 0.;
        for (int k = 0; k < 3; k++) {
          double dsA = dsigmadA(ρ, cs2, A, G, A_devG, d, k, i, j);
          ret(2 + k, 5 + ind) = -dsA;
          tmp -= v(k) * dsA;
        }
        ret(1, 5 + ind) = tmp;
      }
    ret(1, 0) -= σρ.dot(v);
    ret.block<1, 3>(1, 2) -= σ;
    ret.block<1, 9>(1, 5) += ρ * vd * Vec9Map(ψ_.data());
    ret.block<3, 1>(2, 0) -= σρ;
    ret.block<1, 3>(5 + d, 2) = A.row(0);
    ret.block<1, 3>(8 + d, 2) = A.row(1);
    ret.block<1, 3>(11 + d, 2) = A.row(2);
    ret.block<1, 3>(5 + d, 5) = v;
    ret.block<1, 3>(8 + d, 8) = v;
    ret.block<1, 3>(11 + d, 11) = v;
  }
  if (THERMAL) {

    double cα2 = MP.cα2;
    double T = temperature_prim(ρ, p, MP);
    double Tρ = dTdρ(ρ, p, MP);
    double Tp = dTdp(ρ, MP);
    Vec3 J = get_ρJ(Q) / ρ;
    Vec3 H = dEdJ(Q, MP);

    ret(1, 0) += Tρ * H(d);
    ret(1, 1) += Tp * H(d);
    ret.block<1, 3>(1, 14) = ρvd * H;
    ret(1, 14 + d) += cα2 * T;
    ret.block<3, 1>(14, 0) = v(d) * J;
    ret(14 + d, 0) += Tρ;
    ret(14 + d, 1) = Tp;
    ret.block<3, 1>(14, 2 + d) = ρ * J;
    for (int i = 14; i < 17; i++)
      ret(i, i) = ρvd;
  }

  if (MULTI) {
    double λ = Q(mV) / ρ;
    ret(mV, 0) = v(d) * λ;
    ret(mV, 2 + d) = ρ * λ;
    ret(mV, mV) = ρvd;

    if (MP.REACTION > -1)
      ret(1, mV) = MP.Qc * ρvd;
  }
  return ret;
}

MatV_V dPdQ(VecVr Q, Par &MP) {
  // Returns Jacobian of primitive vars with respect to conserved vars
  MatV_V ret = MatV_V::Identity();

  double ρ = Q(0);
  double E = Q(1) / ρ;
  Vec3 v = get_ρv(Q) / ρ;
  Vec3 J;

  double Eρ = dEdρ(Q, MP);
  double Ep = dEdp(Q, MP);
  double Γ_ = 1 / (ρ * Ep);

  double tmp = v.squaredNorm() - (E + ρ * Eρ);
  if (THERMAL) {
    J = get_ρJ(Q) / ρ;
    double cα2 = MP.cα2;
    tmp += cα2 * J.squaredNorm();
  }
  double Υ = Γ_ * tmp;

  ret(1, 0) = Υ;
  ret(1, 1) = Γ_;
  ret.block<1, 3>(1, 2) = -Γ_ * v;
  ret.block<3, 1>(2, 0) = -v / ρ;

  for (int i = 2; i < 5; i++)
    ret(i, i) = 1 / ρ;

  if (VISCOUS) {
    Mat3_3 ψ_ = dEdA(Q, MP);
    ret.block<1, 9>(1, 5) = -Γ_ * ρ * Vec9Map(ψ_.data());
  }
  if (THERMAL) {
    Vec3 H = dEdJ(Q, MP);
    ret.block<1, 3>(1, 14) = -Γ_ * H;
    ret.block<3, 1>(14, 0) = -J / ρ;
    for (int i = 14; i < 17; i++)
      ret(i, i) = 1 / ρ;
  }
  if (MULTI) {
    double λ = Q(mV) / ρ;
    ret(mV, 0) = -λ / ρ;
    ret(mV, mV) = 1 / ρ;

    if (MP.REACTION > -1) {
      double Qc = MP.Qc;
      ret(1, 0) += Γ_ * Qc * λ;
      ret(1, mV) = -Γ_ * Qc;
    }
  }
  return ret;
}
