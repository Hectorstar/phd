#ifndef ITERATOR_H
#define ITERATOR_H

#include "../etc/types.h"
#include "../system/objects.h"

void make_u(Vecr u, std::vector<Vec> &grids, std::vector<bVec> &masks,
            std::vector<Par> &MPs);

double timestep(std::vector<Vec> &grids, std::vector<bVec> &masks, aVecr dX,
                double CFL, double t, double tf, int count,
                std::vector<Par> &MPs, int nmat);

std::vector<Vec> iterator(Vecr u, double tf, iVecr nX, aVecr dX, double CFL,
                          iVecr boundaryTypes, bool SPLIT, bool HALF_STEP,
                          bool STIFF, int FLUX, std::vector<Par> &MPs,
                          double contorted_tol);

#endif // ITERATOR_H
