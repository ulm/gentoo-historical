# this is some test SL code to make sure my fucking parser works (which it
# doesn't)

object test_object
	test_int as integer size 32
	test_char as character encoding utf_8
	test_math as flow some_math
	
	test_set exposes test_math.input
	
	test_math.output.integer_value writes test_int
	test_math.output.char_value writes test_char
end test_object

flow some_math 
end some_math
