#include <cmath>

#include "../../etc/globals.h"
#include "../functions/matrices.h"
#include "../functions/vectors.h"
#include "../variables/state.h"
#include "../waves/shear.h"

double theta1inv(VecVr Q, Par &MP) {
  // Returns the relaxation parameter for the distortion tensor

  // TODO: implement mixing of μ

  double ρ = Q(0);
  Mat3_3Map A = get_A(Q);

  double A53 = pow(A.determinant(), 5. / 3.);
  double cs2 = c_s2(ρ, MP);
  double n = MP.n;

  double sn;
  if (MP.SOLID) {

    if (MP.POWER_LAW) {

      Mat3_3 σ = sigma(Q, MP);
      sn = sigma_norm(σ);
      sn = std::min(sn, 1e8); // Hacky fix

      double σY = MP.σY;
      return 3 * A53 / (cs2 * MP.τ0) * pow((sn / σY), n);
    } else
      return 0.;
  } else {
    double c = A53 * MP.ρ0 / (2 * std::pow(MP.μ, 1 / n));

    if (MP.POWER_LAW) {
      Mat3_3 σ = sigma(Q, MP);
      sn = σ.norm() / sqrt(2.);

      return c * pow(sn, (1 - n) / n);
    } else
      return c;
  }
}

double theta2inv(VecVr Q, Par &MP) {
  // Returns the relaxation parameter for the thermal impulse vector

  // TODO: implement mixing of κ

  double ρ = Q(0);
  double p = pressure(Q, MP);
  double T = temperature(ρ, p, MP);
  return T / (MP.κ * ρ);
}

void f_body(Vec3r x, Par &MP) { x = MP.δp; }

double reaction_rate(VecVr Q, Par &MP) { return 0.; }
