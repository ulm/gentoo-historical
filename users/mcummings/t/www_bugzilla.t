use strict;
use warnings;
use Test::More qw(no_plan);
use File::Spec::Functions qw(catfile);

BEGIN {use_ok('WWW::Bugzilla');}

my $server = 'landfill.bugzilla.org/bugzilla-stable';
my $email = 'krang_test@yahoo.com';
my $password = 'shredder';
my $product = 'FoodReplicator';

my $bz = WWW::Bugzilla->new(    server => $server,
                                email => $email,
                                password => $password,
                                product => $product );

is( $bz->product, $product, "Test for simple field set: $product" );

my @components = $bz->available('component');
$bz->component($components[0]);

my @versions = $bz->available('version');
$bz->version($versions[0]);

$bz->os('Linux');
$bz->platform('PC');
$bz->assigned_to($email);
$bz->summary("This is the summary");
$bz->description("Description here!!!!!!!!!!!!!!!!!!!!!");
my $bug_number = $bz->commit;

like ($bug_number, qr/\d+/, "Returned bug number $bug_number");

my $ubz = WWW::Bugzilla->new(   server => $server,
                                email => $email,
                                password => $password,
                                bug_number => $bug_number );

is( $ubz->summary, "This is the summary", "check for summary text");

$ubz->additional_comments( "comments here");

$ubz->commit;

my $filepath = './Bugzilla.pm';
$ubz->add_attachment(   filepath => $filepath,
                        description => 'this is attach desc' );

$ubz->change_status('fixed');

$ubz->commit;

$ubz->change_status('reopen');

$ubz->commit;

$ubz->mark_as_duplicate('926');

$ubz->commit;
