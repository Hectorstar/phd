#include "../../etc/types.h"
#include "../../scipy/poly.h"

Mat kron(std::vector<Mat> &mats) {
  int idx = mats.size();
  int m0 = mats[idx - 2].rows();
  int m1 = mats[idx - 1].rows();
  int n0 = mats[idx - 2].cols();
  int n1 = mats[idx - 1].cols();
  Mat ret(m0 * m1, n0 * n1);

  for (int i0 = 0; i0 < m0; i0++)
    for (int i1 = 0; i1 < m1; i1++) {
      int i = i0 * m1 + i1;
      for (int j0 = 0; j0 < n0; j0++)
        for (int j1 = 0; j1 < n1; j1++) {
          int j = j0 * n1 + j1;
          ret(i, j) = mats[idx - 2](i0, j0) * mats[idx - 1](i1, j1);
        }
    }
  if (mats.size() == 2) {
    return ret;
  } else {
    mats.pop_back();
    mats[idx - 2] = ret;
    return kron(mats);
  }
}

MatN_N end_value_products(const std::vector<poly> &basis) {
  // ret[i,j] = ψ_i(1) * ψ_j(1)
  MatN_N ret;
  int N = basis.size();
  for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++)
      ret(i, j) = basis[i].eval(1) * basis[j].eval(1);
  return ret;
}

MatN_N derivative_products(const std::vector<poly> &basis, const VecN nodes,
                           const VecN wghts) {
  // ret[i,j] = < ψ_i , ψ_j' >
  MatN_N ret;
  int N = basis.size();
  for (int i = 0; i < N; i++)
    for (int j = 0; j < N; j++) {
      if (i == j)
        ret(i, j) = (pow(basis[i].eval(1), 2.) - pow(basis[i].eval(0), 2.)) / 2;
      else
        ret(i, j) = wghts[i] * basis[j].diff(1).eval(nodes[i]);
    }
  return ret;
}
