#!/usr/bin/perl -w
# Submission script for the CFLAGS/cpuinfo collection project
# Submits data to the web form on http://slinky.surrey.sfu.ca/~robbat2/cflagcollect/
# Requires your email address as a parameter
# Assumes that you don't mind your system info being public
use LWP;
use LWP::UserAgent;

# A little helper func I found on the net.
sub URLEncode {
	my $theURL = $_[0];
	$theURL =~ s/([\W])/"%" . uc(sprintf("%2.2x",ord($1)))/eg;
	return $theURL;
}

# check for valid email address
$argc = @ARGV;
if($argc == 0 or !($ARGV[0] =~ /\@/)) {
$s = "That isn't a valid email address!\nPlease run this program as '$0 emailaddress'\nEG: '$0 foo\@bar.com'\n";
die $s;
}
# This is ALL of the data we collect from the system
print "This may take up to 30 seconds depending on your CPU speed and RAM.\n";
print "Collecting data ";
$email = $ARGV[0];
print ".";
$machinename = `uname -n`;
print ".";
$cflags = `emerge info  2>&1|grep CFLAGS|cut -d= -f2-|xargs`;
print ".";
$cxxflags = `emerge info  2>&1|grep CXXFLAGS|cut -d= -f2-|xargs`;
print ".";
$chost = `emerge info  2>&1|grep CHOST|cut -d= -f2-|xargs`;
print ".";
$gccver = `gcc -v 2>&1`;
print ".";
$binver = `ld -v`;
print ".";
$cpuinfo = `cat /proc/cpuinfo`;
print "Done!\n";

print "Processing data ";
%data = ( 
'email'=>$email,
'machinename'=>$machinename,
'public'=>'on',
'cflags'=>$cflags,
'chost',$chost,
'cxxflags'=>$cxxflags,
'gccver'=>$gccver,
'binver'=>$binver,
'cpuinfo'=>$cpuinfo
);
print ".";
@alldata = sort(keys(%data));
print ".";
$str = 'submit=submit';
print ".";
foreach $key(@alldata) {
	print ".";
	$str .= "&".$key."=".URLEncode("$data{$key}");
}
print "Done!\n";
print "Sending data ";

# Create a user agent object
$ua = LWP::UserAgent->new;
print ".";
$ua->agent("CflagsSubmitted/0.2");
print ".";
#
## Create a request
#$target = 'http://slinky.surrey.sfu.ca/~robbat2/cflagcollect/';
$target = 'http://gentoo.slinky.surrey.sfu.ca/cflagcollect/';
$file = 'submit.php';
my $req = HTTP::Request->new(POST => $target . $file .'?'.$str);
print ".";
$req->content_type('application/x-www-form-urlencoded');
print ".";
$req->content($str);
print ".";

# Pass request to the user agent and get a response back
my $res = $ua->request($req);
print "Done!\n";

# Check the outcome of the response
if ($res->is_success) {
	#print $res->content;
	if($res->content =~ /Done/) {
		print "Data sent successfully\n";
	} else {
		print "Error on the server side!\n";
	print $res->content;
	}
} else {
	print "Error sending data on this side!\n";
}

#print "Content-type: text/html\n\n"; 
#use HTTP::Request::Common qw(POST); 
#use LWP::UserAgent; 
#
#$ua2 = LWP::UserAgent->new(); 
#$ua2->agent("CflagsSubmitted/0.1 ");
#my $req = POST 'http://slinky.surrey.sfu.ca/~robbat2/cflagcollect/', 
#[ first_name => $firstname, email => $email]; 
#
#$content = $ua2->request($req)->as_string; 
#
#print "content = $content"; 



