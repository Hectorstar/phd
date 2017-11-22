#include <string>
#include <sstream>

#include "../include/pybind11/pybind11.h"

#include "types.h"


void print(Matr M)
{
    std::ostringstream oss;

    if (M.cols()==1)
        M = M.transpose();
    else
        oss << "[";

    for (int i=0; i<M.rows(); i++)
    {
        oss << "[";
        for (int j=0; j<M.cols(); j++)
        {
            if (j>0)
                oss << ",";
            oss << M(i,j);
        }
        oss << "]";
        if (i<M.rows()-1)
            oss << ",\n";
    }

    if (M.rows()>1)
        oss << "]";

    pybind11::print(oss.str());
}

void print(double x)
{
    pybind11::print(x);
}

void print(std::string x)
{
    pybind11::print(x);
}