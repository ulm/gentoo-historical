/* { dg-do compile } */
/* { dg-options "-fstack-protector" } */
void
test1()
{
  void intest1(int *a)
    {
      *a ++;
    }
  
  char buf[80];

  buf[0] = 0;
} /* { dg-bogus "not protecting function: it contains functions" } */

void
test2(int n)
{
  char buf[80];
  char vbuf[n];

  buf[0] = 0;
  vbuf[0] = 0;
} /* { dg-bogus "not protecting variables: it has a variable length buffer" } */

void
test3()
{
  char buf[5];

  buf[0] = 0;
} /* { dg-bogus "not protecting function: buffer is less than 8 bytes long" } */
