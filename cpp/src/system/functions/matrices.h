#ifndef MATRICES_H
#define MATRICES_H

#include "../../etc/types.h"
#include "../objects.h"

Mat3_3 AdevG(Mat3_3r A);
double devGsq(Mat3_3r A);
double sigma_norm(Mat3_3r σ);
void destress(VecVr Q);

#endif
