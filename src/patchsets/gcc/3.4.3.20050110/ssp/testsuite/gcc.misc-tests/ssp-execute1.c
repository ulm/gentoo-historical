/* Test location changes of character array.  */

void
test(int i)
{
  int  ibuf1[10];
  char buf[50];
  int  ibuf2[10];
  char buf2[50000];
  int  ibuf3[10];
  char *p;

  /* c1: the frame offset of buf[0]
     c2: the frame offset of buf2[0]
  */
  p= &buf[0]; *p=1;		/* expected rtl: (+ fp -c1) */
  if (*p != buf[0])
    abort();
  p= &buf[5]; *p=2;		/* expected rtl: (+ fp -c1+5) */
  if (*p != buf[5])
    abort();
  p= &buf[-1]; *p=3;		/* expected rtl: (+ (+ fp -c1) -1) */
  if (*p != buf[-1])
    abort();
  p= &buf[49]; *p=4;		/* expected rtl: (+ fp -c1+49) */
  if (*p != buf[49])
    abort();
  p = &buf[i+5]; *p=5;		/* expected rtl: (+ (+ fp -c1) (+ i 5)) */
  if (*p != buf[i+5])
    abort ();
  p = buf - 1; *p=6;		/* expected rtl: (+ (+ fp -c1) -1) */
  if (*p != buf[-1])
    abort ();
  p = 1 + buf; *p=7;		/* expected rtl: (+ (+ fp -c1) 1) */
  if (*p != buf[1])
    abort ();
  p = &buf[1] - 1; *p=8;	/* expected rtl: (+ (+ fp -c1+1) -1) */
  if (*p != buf[0])
    abort ();

  /* test big offset which is greater than the max value of signed 16 bit integer.  */
  p = &buf2[45555]; *p=9;	/* expected rtl: (+ fp -c2+45555) */
  if (*p != buf2[45555])
    abort ();
}

int main()
{
  test(10);
  exit(0);
}


  
