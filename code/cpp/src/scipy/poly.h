#ifndef POLY_H
#define POLY_H

#include "../etc/types.h"

Vec integrate(Vec p);
Vec differentiate(Vec p);
double evaluate(Vec p, double x);
Vec multiply(Vec p1, Vec p2);

class poly {
public:
  poly();
  poly(Vec c);
  Vec coef;

  poly intt() const;
  poly diff(int n) const;
  double eval(double x) const;

  poly operator/(double c);
  poly operator*(const poly &p);
};

#endif // POLY_H
