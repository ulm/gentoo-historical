===================================================================
RCS file: /cvs/gcc/gcc/gcc/cp/init.c,v
retrieving revision 1.412.2.9
retrieving revision 1.412.2.10
diff -u -r1.412.2.9 -r1.412.2.10
--- gcc/gcc/cp/init.c	2005/09/06 15:01:00	1.412.2.9
+++ gcc/gcc/cp/init.c	2005/09/22 00:09:41	1.412.2.10
@@ -1566,12 +1566,8 @@
 tree
 integral_constant_value (tree decl)
 {
-  while ((TREE_CODE (decl) == CONST_DECL
-	  || (TREE_CODE (decl) == VAR_DECL
-	      /* And so are variables with a 'const' type -- unless they
-		 are also 'volatile'.  */
-	      && CP_TYPE_CONST_NON_VOLATILE_P (TREE_TYPE (decl))
-	      && DECL_INITIALIZED_BY_CONSTANT_EXPRESSION_P (decl))))
+  while (TREE_CODE (decl) == CONST_DECL
+	 || DECL_INTEGRAL_CONSTANT_VAR_P (decl))
     {
       tree init;
       /* If DECL is a static data member in a template class, we must
