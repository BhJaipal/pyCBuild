#include "py-math.h"

int square(int x) { return x * x; }
int cube(int x) { return x * x * x; }

int factorial(int x) {
  if (x == 0)
    return 1;
  if (x == 1)
    return 1;
  if (x < 0)
    return 0;
  return x * factorial(x - 1);
}