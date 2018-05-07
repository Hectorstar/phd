#include "../../include/eigen3/SVD"
#include "../etc/globals.h"
#include "functions/matrices.h"
#include "functions/vectors.h"
#include "variables/eos.h"
#include <cmath>

double pos(double x) { return std::max(0., x); }

void analyticSolver_distortion(VecVr Q, double dt, Par &MP) {
  Mat3_3Map A(Q.data() + 5);
  Eigen::JacobiSVD<Mat3_3> svd(A, Eigen::ComputeFullV | Eigen::ComputeFullU);

  Vec3 s = svd.singularValues();
  double detA = s(0) * s(1) * s(2);
  double detA1_3 = cbrt(detA);
  double detA2_3 = detA1_3 * detA1_3;
  double s0 = s(0) * s(0) / detA2_3;
  double s1 = s(1) * s(1) / detA2_3;
  double s2 = s(2) * s(2) / detA2_3;

  double m0 = (s0 + s1 + s2) / 3;
  double u0 =
      ((s0 - s1) * (s0 - s1) + (s1 - s2) * (s1 - s2) + (s2 - s0) * (s2 - s0)) /
      3.;

  if (u0 >= 1e-12) {

      double τ = 2 * detA * detA * detA1_3 / MP.τ1 * dt;

      double c0 = exp(-9 * τ);
      double c1 = (9 * m0 - u0 - 9) * exp(3 * τ);
      double c2 = 6 * m0 - u0 - 6;
      double m = 1 + c0 / 3 * (c1 - c2);
      double u = pos(c0 * (2 * c1 - 3 * c2));

      double Δ = -2 * m * m * m + m * u + 2;
      double arg1 = pos(6 * u * u * u - 81 * Δ * Δ);
      double θ;

      if (arg1 < 1e-12)
          θ = 0.;
      else if (abs(Δ) < 1e-12)
          θ = sgn(Δ) * M_PI / 2;
      else
          θ = atan(sqrt(arg1) / (9. * Δ));

      double x1 = sqrt(6 * u) / 3 * cos(θ / 3) + m;
      double tmp = 3 * m - x1;
      double arg2 = pos(x1 * tmp * tmp - 4);
      double x2 = 0.5 * (sqrt(arg2 / x1) + tmp);
      double x3 = 1 / (x1 * x2);

      double x[3]{x1, x2, x3};
      std::sort(x, x + 3); // sorts in ascending order
      Mat3_3 Vmat = svd.matrixV().transpose();

      for (int i = 0; i < 3; i++)
        Vmat.row(i) *= detA1_3 * sqrt(x[2 - i]); // s sorted in descending order

      A.noalias() = svd.matrixU() * Vmat;

  }
}

void analyticSolver_thermal(VecVr Q, double dt, Par &MP) {
  // Solves the thermal impulse ODE analytically in 3D for the ideal gas EOS
  double ρ = Q(0);
  double E = Q(1) / ρ;
  Vec3 v = get_ρv(Q) / ρ;
  Mat3_3Map A = get_A(Q);
  Vec3Map ρJ = get_ρJ(Q);

  double c1 = E - E_2A(ρ, A, MP) - E_3(v);
  double c2 = MP.cα2 / 2.;
  double k = 2 * MP.ρ0 / (MP.τ2 * MP.T0 * ρ * MP.cv);
  c1 *= k;
  c2 *= k;

  double ea = exp(-c1 * dt / 2);
  double den = 1 - c2 / c1 * (1 - ea * ea) * ρJ.squaredNorm() / (ρ * ρ);
  Q.segment<3>(14) *= ea / sqrt(den);
}

void ode_stepper_analytic(VecVr Q, double dt, Par &MP) {
  // Solves the ODE analytically by linearising the distortion equations and
  // providing an analytic approximation to the thermal impulse evolution

  if (VISCOUS)
    analyticSolver_distortion(Q, dt, MP);
  if (THERMAL)
    analyticSolver_thermal(Q, dt, MP);
}