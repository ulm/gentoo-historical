void
test(int i, char *j, int k)
{
  int  a[10];
  char b;
  int  c;
  long *d;
  char buf[50];
  long e[10];
  int  n;

  a[0] = 4;
  b = 5;
  c = 6;
  d = (long*)7;
  e[0] = 8;

  /* overflow buffer */
  for (n = 0; n < 120; n++)
    buf[n] = 0;
  
  if (j == 0 || *j != 2)
    abort ();
  if (a[0] == 0)
    abort ();
  if (b == 0)
    abort ();
  if (c == 0)
    abort ();
  if (d == 0)
    abort ();
  if (e[0] == 0)
    abort ();

  exit (0);
}

int main()
{
  int i, k;
  int j[40];
  i = 1;
  j[39] = 2;
  k = 3;
  test(i, &j[39], k);
}


  
